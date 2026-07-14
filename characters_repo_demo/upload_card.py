#!/usr/bin/env python3
"""
cards.sillytavern.one 登录并上传角色卡

登录流程：
1. 访问 cards.sillytavern.one/auth/login → 重定向到 sillytavern.one/sso/jump?to=cards
2. 访问 sillytavern.one/sso/jump?to=cards → 重定向到 sillytavern.one/login
3. 在 sillytavern.one/login 登录 → 设置 st_session cookie
4. 重定向回 cards.sillytavern.one/auth/callback?token=xxx → 设置 connect.sid cookie
5. 使用 connect.sid cookie 访问 cards.sillytavern.one/upload
"""

import requests
import json
import os
import sys
import base64
import struct
import argparse
from urllib3.exceptions import ProtocolError
from pathlib import Path
from dotenv import load_dotenv

# ============ 配置 ============
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ENV_FILE = PROJECT_DIR / ".env"
CARDS_DIR = SCRIPT_DIR / "破局-从冷落走到瞩目"
COOKIE_FILE = SCRIPT_DIR / "cookies.json"

BASE_URL = "https://cards.sillytavern.one"
SSO_URL = "https://sillytavern.one"


def load_credentials():
    """加载登录凭证"""
    load_dotenv(ENV_FILE)
    return {
        'username': os.getenv('characters_repo_username'),
        'password': os.getenv('characters_repo_password')
    }


def login_and_get_cookies():
    """完整登录流程，返回包含两个域 cookie 的字典"""
    creds = load_credentials()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    
    print("步骤 1: 访问 cards.sillytavern.one/auth/login...")
    r = session.get(f"{BASE_URL}/auth/login", allow_redirects=True)
    print(f"  当前 URL: {r.url}")
    
    # 应该重定向到 sillytavern.one/login
    if 'sillytavern.one' in r.url:
        print("步骤 2: 在 sillytavern.one 登录...")
        r = session.post(
            f"{SSO_URL}/login",
            data={
                'username': creds['username'],
                'password': creds['password']
            },
            allow_redirects=True
        )
        print(f"  登录后 URL: {r.url}")
    
    # 检查是否获得 token
    if 'token=' in r.url:
        token = r.url.split('token=')[1].split('&')[0]
        print(f"  获得 SSO token")
    else:
        token = None
    
    # 访问 cards.sillytavern.one/upload 获取 connect.sid cookie
    print("步骤 3: 获取 cards.sillytavern.one session...")
    r = session.get(f"{BASE_URL}/upload")
    
    # 保存 cookies（包括两个域的）
    cookies = {}
    for cookie in session.cookies:
        cookies[cookie.name] = cookie.value
    
    # 手动添加两个域的 cookie
    st_session = cookies.get('st_session')
    connect_sid = cookies.get('connect.sid')
    
    if st_session:
        cookies['st_session'] = st_session
    if connect_sid:
        cookies['connect.sid'] = connect_sid
    
    with open(COOKIE_FILE, 'w') as f:
        json.dump(cookies, f)
    print(f"  保存 cookies: {list(cookies.keys())}")
    
    return cookies


def load_cookies():
    """加载保存的 cookies"""
    if COOKIE_FILE.exists():
        with open(COOKIE_FILE, 'r') as f:
            return json.load(f)
    return None


def verify_chara_chunk(png_path):
    """验证 PNG 文件的 tEXt chunk 格式"""
    with open(png_path, 'rb') as f:
        data = f.read()
    
    pos = 8
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8].decode('ascii', errors='replace')
        chunk_data = data[pos+8:pos+8+length]
        
        if chunk_type == 'tEXt':
            try:
                null1 = chunk_data.index(0x00)
                keyword = chunk_data[:null1].decode()
                rest = chunk_data[null1+1:]
                if 0x00 in rest:
                    null2 = rest.index(0x00)
                    compression_method = rest[0]
                    text = rest[null2+1:]
                    
                    if keyword == 'chara':
                        decoded = base64.b64decode(text)
                        card = json.loads(decoded)
                        return True, card.get('spec')
            except:
                pass
        
        pos += 12 + length
    
    return False, None


def upload_card(cookies, png_path, card_json_path):
    """上传角色卡"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Origin': BASE_URL,
        'Referer': f"{BASE_URL}/upload",
    })
    
    # 设置 cookies
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # 检查是否已登录
    print("  检查登录状态...")
    r = session.get(f"{BASE_URL}/upload")
    if '登录' in r.text or 'login' in r.url.lower():
        print("  ❌ 未登录，需要重新登录")
        return False, "未登录"
    
    # 读取卡片数据
    card_data = {
        'name': png_path.stem,
        'description': ''
    }
    
    if card_json_path and card_json_path.exists():
        with open(card_json_path, 'r', encoding='utf-8') as f:
            v2_card = json.load(f)
            card_data['name'] = v2_card.get('data', {}).get('name', png_path.stem)
            card_data['description'] = v2_card.get('data', {}).get('description', '')[:2000]
    
    # 构建 multipart 表单
    print(f"  上传: {png_path.name}")
    
    boundary = "----WebKitFormBoundary" + "".join(["abcdefghijklmnop"[i%16] for i in range(16)])
    
    # 构建表单数据
    form_data = []
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="card_name"')
    form_data.append('')
    form_data.append(card_data['name'])
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="description"')
    form_data.append('')
    form_data.append(card_data['description'])
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="card_type"')
    form_data.append('')
    form_data.append('original')
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="author"')
    form_data.append('')
    form_data.append(load_credentials()['username'])
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="has_nsfw_content"')
    form_data.append('')
    form_data.append('0')
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="has_nsfw_image"')
    form_data.append('')
    form_data.append('0')
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="orientation"')
    form_data.append('')
    form_data.append('女性向')
    
    for genre in ['现代都市', '校园青春']:
        form_data.append(f'--{boundary}')
        form_data.append('Content-Disposition: form-data; name="cat_genre"')
        form_data.append('')
        form_data.append(genre)
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="cat_content"')
    form_data.append('')
    form_data.append('剧情向')
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="cat_character"')
    form_data.append('')
    form_data.append('人类')
    
    form_data.append(f'--{boundary}')
    form_data.append('Content-Disposition: form-data; name="is_public"')
    form_data.append('')
    form_data.append('1')
    
    form_data.append(f'--{boundary}--')
    
    body = '\r\n'.join(form_data)
    
    # 读取 PNG 文件
    with open(png_path, 'rb') as f:
        png_data = f.read()
    
    # 构建 data 和 files
    data = {
        'card_name': card_data['name'],
        'description': card_data['description'],
        'card_type': 'original',
        'author': load_credentials()['username'],
        'has_nsfw_content': '0',
        'has_nsfw_image': '0',
        'orientation': '女性向',
        'cat_genre': ['现代都市', '校园青春'],
        'cat_content': '剧情向',
        'cat_character': '人类',
        'is_public': '1',
    }
    
    files = {
        'card_file': (png_path.name, png_data, 'image/png')
    }
    
    # 上传大文件需要更长超时，失败时自动重试
    for attempt in range(5):
        try:
            r = session.post(
                f"{BASE_URL}/upload",
                data=data,
                files=files,
                timeout=(90, 300)  # (连接超时, 读取超时 5分钟)
            )
            break
        except (TimeoutError, requests.exceptions.Timeout, ProtocolError) as e:
            if attempt < 4:
                print(f"  ⏳ 上传失败 ({type(e).__name__})，重试中 ({attempt + 1}/5)...")
                continue
            raise
    
    print(f"  响应状态: {r.status_code}")
    
    # 从响应中提取卡片 ID 和 slug
    card_id = None
    card_slug = None
    
    # 方法1: 从 og:image URL 提取数字 ID
    import re
    thumb_match = re.search(r'/api/card/(\d+)/thumb', r.text)
    if thumb_match:
        card_id = thumb_match.group(1)
    
    # 方法2: 从页面 URL 提取 slug
    url_match = re.search(r'/card/([^"\']+)', r.url)
    if url_match:
        card_slug = url_match.group(1)
    
    if card_id:
        card_url = f"https://cards.sillytavern.one/card/{card_id}"
        print(f"  ✅ 卡片数字 ID: {card_id}")
        print(f"  ✅ 卡片 URL: {card_url}")
        
        # 保存卡片信息到角色目录
        save_card_info(card_data['name'], card_id, card_slug, card_url)
    
    # 检查上传结果
    if '角色卡' in r.text and card_data['name'] in r.text:
        return True, f"上传成功，ID: {card_id}"
    elif '错误' in r.text or 'error' in r.text.lower():
        return False, r.text[:500]
    elif r.status_code == 200:
        if 'sillytavern' in r.text.lower():
            return True, f"上传成功，ID: {card_id}"
        return True, f"响应长度: {len(r.text)}"
    else:
        return False, f"状态码: {r.status_code}"


def save_card_info(card_name, card_id, card_slug, card_url):
    """保存上传的卡片信息到角色目录下的 .repo.json 文件"""
    repo_file = CARDS_DIR / f"{card_name}.repo.json"
    
    info = {
        'name': card_name,
        'id': card_id,
        'slug': card_slug,
        'url': card_url,
        'uploaded_at': __import__('datetime').datetime.now().isoformat(),
    }
    
    try:
        with open(repo_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"  💾 已保存到 {repo_file}")
    except Exception as e:
        print(f"  ⚠️ 保存失败: {e}")


def load_card_info(card_name):
    """读取角色的 .repo.json 文件"""
    repo_file = CARDS_DIR / f"{card_name}.repo.json"
    if repo_file.exists():
        with open(repo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def delete_card(session, card_id):
    """删除已上传的卡片（cards.sillytavern.one 无更新接口，只能删除重传）"""
    r = session.post(
        f"{BASE_URL}/api/card/{card_id}/delete-mine",
        timeout=30
    )
    if r.status_code == 200:
        return True
    elif r.status_code == 404:
        # 卡片不存在，可能已被删除
        return True
    else:
        print(f"  ⚠️ 删除失败: {r.status_code} - {r.text[:200]}")
        return False


def main():
    parser = argparse.ArgumentParser(description='上传角色卡到 cards.sillytavern.one')
    parser.add_argument('--card', type=str, help='角色名（不指定则上传所有）')
    parser.add_argument('--relogin', action='store_true', help='强制重新登录')
    args = parser.parse_args()
    
    print("=" * 60)
    print("cards.sillytavern.one 角色卡上传工具")
    print("=" * 60)
    
    # 获取 cookies
    cookies = None
    if not args.relogin:
        cookies = load_cookies()
    
    if not cookies or args.relogin:
        cookies = login_and_get_cookies()
    
    # 确定要上传的角色
    if args.card:
        cards = [args.card]
    else:
        cards = [p.stem for p in CARDS_DIR.glob("*.png") if '叙事者' not in p.stem]
    
    print(f"\n准备上传 {len(cards)} 个角色卡...")
    
    for card_name in cards:
        png_path = CARDS_DIR / f"{card_name}.png"
        json_path = CARDS_DIR / f"{card_name}.json"
        
        if not png_path.exists():
            print(f"\n❌ 文件不存在: {png_path}")
            continue
        
        print(f"\n--- 上传: {card_name} ---")
        
        # 检查是否有已上传的旧版本
        old_info = load_card_info(card_name)
        if old_info and old_info.get('id'):
            print(f"  📋 发现旧版本: ID={old_info['id']}, 正在删除...")
            delete_session = requests.Session()
            delete_session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            })
            for name, value in cookies.items():
                delete_session.cookies.set(name, value, domain='sillytavern.one')
            if delete_card(delete_session, old_info['id']):
                print(f"  ✅ 旧版本已删除")
        
        # 验证 tEXt chunk
        valid, spec = verify_chara_chunk(png_path)
        if valid:
            print(f"  ✓ tEXt chunk 有效 (spec: {spec})")
        else:
            print(f"  ❌ tEXt chunk 无效")
        
        # 上传
        success, message = upload_card(cookies, png_path, json_path)
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
