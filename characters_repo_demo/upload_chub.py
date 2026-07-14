"""
上传角色卡到 chub.ai
用法:
  python upload_chub.py [角色名]          # 上传单个角色（含头像）
  python upload_chub.py                   # 上传全部角色（含头像）
  python upload_chub.py --avatar [角色名]  # 只上传头像（已有角色）
  python upload_chub.py --avatar          # 只上传全部头像（已有角色）
"""
import json, os, sys, time, re, base64
import requests
from pathlib import Path
from dotenv import load_dotenv

# ===== 配置 =====
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ENV_FILE = PROJECT_DIR / ".env"
load_dotenv(ENV_FILE)

CURRENT_STORY = os.getenv("CURRENT_STORY", "破局-从冷落走到瞩目")
AI_STORY_LOCAL_DIR = os.getenv("AI_STORY_LOCAL_DIR", "ai_story/local")
AVATARS_SUBDIR = os.getenv("AVATARS_SUBDIR", "bak1")

BASE_DIR = SCRIPT_DIR / CURRENT_STORY
STORY_DIR = (Path(AI_STORY_LOCAL_DIR) if Path(AI_STORY_LOCAL_DIR).is_absolute() else PROJECT_DIR / AI_STORY_LOCAL_DIR) / CURRENT_STORY

USERNAME = os.getenv("CHUB_USERNAME")
PASSWORD = os.getenv("CHUB_PASSWORD")
GATEWAY = os.getenv("CHUB_GATEWAY", "https://gateway.chub.ai")
RO_API = os.getenv("CHUB_RO_API", "https://ro.chub.ai")

HEADERS_COMMON = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "origin": "https://chub.ai",
    "referer": "https://chub.ai/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}

# ===== 登录 =====
def login():
    print("[登录] 获取 CSRF token...")
    resp = requests.get(f"{GATEWAY}/authentication/token", headers=HEADERS_COMMON, timeout=30)
    resp.raise_for_status()
    csrf_token = resp.json()["csrf_token"]
    print(f"  CSRF: {csrf_token[:20]}...")

    print("[登录] 提交登录...")
    payload = {
        "csrf_token": csrf_token,
        "email_or_username": USERNAME,
        "password": PASSWORD,
        "oauth": None,
        "state": "",
        "redirect_url": "https://chub.ai/login",
        "is_mobile": "false"
    }
    resp = requests.post(
        f"{GATEWAY}/authentication/login",
        headers={**HEADERS_COMMON, "content-type": "application/json"},
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    samwise = data["samwise"]
    print(f"  登录成功! samwise: {samwise[:20]}...")
    return samwise

# ===== 读取角色 JSON =====
def load_character(name):
    json_path = os.path.join(BASE_DIR, f"{name}.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ===== 转换格式：Toonflow JSON → chub.ai API 格式 =====
def toonflow_to_chub(chara_json, avatar_url=""):
    data = chara_json.get("data", chara_json)
    ext = data.get("extensions", {}).get("toonflow", {})

    name = data.get("name", "")
    description = data.get("description", "")
    personality = data.get("personality", "")
    first_message = data.get("first_mes", data.get("first_message", ""))
    scenario = data.get("scenario", "")
    tags = data.get("tags", ["Roleplay"])

    # chub.ai 需要 tagline（短描述）
    tagline = description[:100] if description else ""

    # in_chat_name 默认同 name
    in_chat_name = name

    # alternate_greetings
    alt_greetings = data.get("alternate_greetings", [])
    if alt_greetings is None:
        alt_greetings = []

    payload = {
        "name": name,
        "avatar": avatar_url,
        "tagline": tagline,
        "in_chat_name": in_chat_name,
        "description": description,
        "tags": tags if tags else ["Roleplay"],
        "is_public": True,
        "is_nsfw": False,
        "is_anonymous": False,
        "personality": personality,
        "first_message": first_message,
        "scenario": scenario,
        "example_dialogs": data.get("mes_example", ""),
        "voice_id": None,
        "alternate_greetings": alt_greetings,
        "system_prompt": "",
        "post_history_instructions": "",
        "depth_prompt": {"depth": 0, "prompt": ""},
        "embedded_lorebook": None,
        "is_unlisted": False,
        "extensions": {"depth_prompt": {"depth": 0, "prompt": ""}},
        "character_book": None,
        "character_id": -1,
    }
    return payload

# ===== 上传头像 =====
def upload_avatar(samwise, name, repo_data):
    """通过 PUT avatar base64 上传头像，返回是否成功"""
    slug = repo_data.get("slug", "")
    char_id = repo_data.get("id", "")
    png_path = os.path.join(BASE_DIR, f"{name}.png")

    if not os.path.exists(png_path):
        print(f"  (无头像 PNG，跳过)")
        return True  # 不算失败

    headers = {
        **HEADERS_COMMON,
        "ch-api-key": samwise,
        "samwise": samwise,
        "content-type": "application/json",
    }

    with open(png_path, "rb") as f:
        img_data = f.read()
    b64 = base64.b64encode(img_data).decode("ascii")
    avatar_b64 = f"data:image/png;base64,{b64}"

    # 1. 完整头像
    url1 = f"{GATEWAY}/api/core/characters/{USERNAME}/{slug}"
    resp1 = requests.put(url1, headers=headers, json={"avatar": avatar_b64, "character_id": int(char_id)}, timeout=60)
    print(f"  头像 PUT core: {resp1.status_code} {'✅' if resp1.status_code == 200 else '❌'}")

    # 2. 搜索缩略图
    url2 = f"{GATEWAY}/api/project/{char_id}/metadata"
    resp2 = requests.put(url2, headers=headers, json={"avatar": avatar_b64}, timeout=60)
    print(f"  头像 PUT meta: {resp2.status_code} {'✅' if resp2.status_code == 200 else '❌'}")

    return resp1.status_code == 200 and resp2.status_code == 200

# ===== 上传角色 =====
def upload_character(samwise, name):
    print(f"\n{'='*60}")
    print(f"[上传] {name}")

    chara = load_character(name)
    data = chara.get("data", chara)
    ext = data.get("extensions", {}).get("toonflow", {})

    # 检查是否已存在
    repo_path = os.path.join(BASE_DIR, f"{name}.repo.chub_ai.json")
    existing_slug = None
    existing_id = None
    if os.path.exists(repo_path):
        with open(repo_path, "r", encoding="utf-8") as f:
            repo_data = json.load(f)
        existing_slug = repo_data.get("slug", "").split("/")[-1]
        existing_id = repo_data.get("id", "")

    # 头像：优先用已有的 chub.ai URL
    avatar_url = ""
    if existing_slug:
        avatar_url = f"https://avatars.charhub.io/avatars/{USERNAME}/{existing_slug}/chara_card_v2.png"

    payload = toonflow_to_chub(chara, avatar_url)

    headers = {
        **HEADERS_COMMON,
        "ch-api-key": samwise,
        "samwise": samwise,
        "content-type": "application/json",
    }

    if existing_slug:
        # 更新
        print(f"  更新已有角色: {existing_slug}")
        url = f"{GATEWAY}/api/core/characters/{USERNAME}/{existing_slug}"
        resp = requests.put(url, headers=headers, json=payload, timeout=60)
    else:
        # 新建
        print(f"  创建新角色...")
        url = f"{GATEWAY}/api/core/characters"
        resp = requests.post(url, headers=headers, json=payload, timeout=60)

    print(f"  状态码: {resp.status_code}")
    if resp.status_code in (200, 201):
        result = resp.json()
        print(f"  成功! 返回: {json.dumps(result, ensure_ascii=False)[:200]}")

        # 从响应中提取 slug 和 avatar URL
        slug = result.get("slug", existing_slug or "")
        avatar = result.get("avatar", "")
        char_id = result.get("id", existing_id or "")

        # 如果响应没有 slug，尝试从 API 获取
        if not slug and existing_slug:
            slug = existing_slug

        repo_data = {
            "name": name,
            "id": str(char_id),
            "slug": slug,
            "url": f"https://chub.ai/characters/{USERNAME}/{slug}" if slug else "",
            "avatar": avatar,
            "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(repo_path, "w", encoding="utf-8") as f:
            json.dump(repo_data, f, ensure_ascii=False, indent=2)
        print(f"  已保存到 {name}.repo.chub_ai.json")

        # 上传头像
        if slug:
            repo_path = os.path.join(BASE_DIR, f"{name}.repo.chub_ai.json")
            with open(repo_path, "r", encoding="utf-8") as f:
                updated_repo = json.load(f)
            upload_avatar(samwise, name, updated_repo)

        return True
    else:
        print(f"  失败: {resp.status_code}")
        print(f"  {resp.text[:500]}")
        return False

# ===== 列出所有角色文件 =====
def list_characters():
    chars = []
    for fname in os.listdir(BASE_DIR):
        if not fname.endswith(".json"):
            continue
        # 跳过非角色文件
        if fname.startswith("INDEX") or fname.startswith("世界书") or fname.startswith("旁白"):
            continue
        # 只处理真正的角色 JSON（不含 .repo）
        if ".repo" in fname:
            continue
        name = fname[:-5]  # 去掉 .json
        chars.append(name)
    return sorted(chars)

# ===== 主函数 =====
def main():
    samwise = login()

    # --avatar 模式：只上传头像
    if len(sys.argv) > 1 and sys.argv[1] == "--avatar":
        names = list_characters() if len(sys.argv) == 2 else [sys.argv[2]]
        print(f"\n只上传头像，共 {len(names)} 个角色\n")
        for i, name in enumerate(names, 1):
            repo_path = os.path.join(BASE_DIR, f"{name}.repo.chub_ai.json")
            if not os.path.exists(repo_path):
                print(f"[{i}/{len(names)}] {name}: 无 repo 文件，跳过")
                continue
            with open(repo_path, "r", encoding="utf-8") as f:
                repo_data = json.load(f)
            print(f"[{i}/{len(names)}] 上传头像: {name}")
            ok = upload_avatar(samwise, name, repo_data)
            print(f"  {'✅ 成功' if ok else '❌ 失败'}\n")
            time.sleep(1)
    else:
        # 普通模式：上传角色+头像
        if len(sys.argv) > 1:
            names = [sys.argv[1]]
        else:
            names = list_characters()

        print(f"\n上传角色+头像，共 {len(names)} 个角色: {names}")

        for i, name in enumerate(names, 1):
            print(f"\n[{i}/{len(names)}] 处理: {name}")
            ok = upload_character(samwise, name)
            if not ok:
                print(f"  ⚠️ 上传失败，跳过")
            time.sleep(2)  # 避免请求过快

    print("\n全部完成!")

if __name__ == "__main__":
    main()
