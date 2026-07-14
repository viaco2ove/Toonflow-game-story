#!/usr/bin/env python3
"""
上传角色卡到 cards.sillytavern.one

用法:
    python upload_to_cards.py [--card 角色名]
"""

import requests
import json
import os
import base64
import struct
from pathlib import Path
from dotenv import load_dotenv

# ============ 配置 ============
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ENV_FILE = PROJECT_DIR / ".env"
CARDS_DIR = SCRIPT_DIR / "破局-从冷落走到瞩目"

# 加载 .env
load_dotenv(ENV_FILE)

BASE_URL = "https://cards.sillytavern.one"
USERNAME = os.getenv("characters_repo_username")
PASSWORD = os.getenv("characters_repo_password")

print(f"Username: {USERNAME}")
print(f"Cards dir: {CARDS_DIR}")


def parse_env_file(env_path):
    """解析 .env 文件"""
    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                # 移除引号
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                env_vars[key] = value
    return env_vars


def login(session):
    """登录 cards.sillytavern.one"""
    login_url = f"{BASE_URL}/auth/login"
    
    # 获取登录页面（获取 CSRF token）
    response = session.get(login_url)
    print(f"Login page status: {response.status_code}")
    
    # 发送登录请求
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    print(f"Login response status: {response.status_code}")
    print(f"Login response URL: {response.url}")
    
    # 检查是否登录成功
    if "login" not in response.url.lower():
        print("✅ 登录成功！")
        return True
    else:
        print("❌ 登录失败")
        return False


def get_csrf_token(session, url):
    """从页面获取 CSRF token"""
    response = session.get(url)
    # 通常在 meta 标签或脚本中
    import re
    csrf_match = re.search(r'name="csrf-token"\s+content="([^"]+)"', response.text)
    if csrf_match:
        return csrf_match.group(1)
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
            # 解析 tEXt chunk
            try:
                null1 = chunk_data.index(0x00)
                keyword = chunk_data[:null1].decode()
                rest = chunk_data[null1+1:]
                if 0x00 in rest:
                    null2 = rest.index(0x00)
                    compression_method = rest[0]
                    text = rest[null2+1:]
                    
                    if keyword == 'chara':
                        # 验证可以解码
                        decoded = base64.b64decode(text)
                        card = json.loads(decoded)
                        print(f"  ✓ keyword: {keyword}, compression: {compression_method}, spec: {card.get('spec')}")
                        return True
            except Exception as e:
                print(f"  ✗ tEXt chunk 解析失败: {e}")
                return False
        
        pos += 12 + length
    
    print("  ✗ 未找到 tEXt chunk")
    return False


def upload_card(session, png_path, card_data):
    """上传角色卡"""
    upload_url = f"{BASE_URL}/upload"
    
    # 准备表单数据
    files = {
        'card_file': (png_path.name, open(png_path, 'rb'), 'image/png')
    }
    
    data = {
        'card_name': card_data.get('name', png_path.stem),
        'description': card_data.get('description', ''),
        'card_type': 'original',
        'author': USERNAME,
        'source_url': '',
        'has_nsfw_content': '0',
        'has_nsfw_image': '0',
        'orientation': '女性向',
        'cat_genre': ['现代都市', '校园青春'],
        'cat_content': '剧情向',
        'cat_character': '人类',
        'custom_tag_1': 'N',
        'custom_tag_2': '',
        'custom_tag_3': '',
        'is_public': '1',
    }
    
    print(f"  上传文件: {png_path.name}")
    print(f"  角色名: {data['card_name']}")
    
    response = session.post(upload_url, files=files, data=data)
    print(f"  响应状态: {response.status_code}")
    print(f"  响应内容: {response.text[:500]}")
    
    return response


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='上传角色卡到 cards.sillytavern.one')
    parser.add_argument('--card', type=str, help='角色名（不指定则上传所有）')
    args = parser.parse_args()
    
    # 创建 session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    })
    
    # 登录
    if not login(session):
        print("登录失败，退出")
        return
    
    # 确定要上传的角色
    if args.card:
        cards = [args.card]
    else:
        # 上传所有 PNG 文件
        cards = [p.stem for p in CARDS_DIR.glob("*.png") if p.stem != "旁白-叙事者"]
    
    print(f"\n准备上传 {len(cards)} 个角色卡...")
    
    for card_name in cards:
        png_path = CARDS_DIR / f"{card_name}.png"
        json_path = CARDS_DIR / f"{card_name}.json"
        
        if not png_path.exists():
            print(f"\n❌ 文件不存在: {png_path}")
            continue
        
        print(f"\n--- 上传: {card_name} ---")
        
        # 验证 tEXt chunk
        print("验证 tEXt chunk...")
        verify_chara_chunk(png_path)
        
        # 读取 JSON 配置
        card_data = {}
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                v2_card = json.load(f)
                card_data = {
                    'name': v2_card.get('data', {}).get('name', card_name),
                    'description': v2_card.get('data', {}).get('description', '')[:500],
                }
        
        # 上传
        upload_card(session, png_path, card_data)
        
        # 关闭文件
        files = {'card_file': (png_path.name, open(png_path, 'rb'), 'image/png')}
        files['card_file'][1].close()


if __name__ == "__main__":
    main()
