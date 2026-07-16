"""
cards.sillytavern.one 上传客户端

登录流程:
1. 访问 cards.sillytavern.one/auth/login -> 重定向到 sillytavern.one/sso/jump
2. 在 sillytavern.one/login 登录 -> 设置 st_session cookie
3. 重定向回 cards.sillytavern.one/auth/callback?token=xxx -> 设置 connect.sid cookie
4. 使用 connect.sid cookie 上传

上传: POST /upload, multipart/form-data
删除: POST /api/card/{id}/delete-mine
"""
import json
import os
import time
import struct
import base64
import re
from pathlib import Path

import requests
from urllib3.exceptions import ProtocolError

from src.config import GlobalConfig, StoryConfig, load_config
from src.png_utils import verify_chara_chunk


class SillyTavernCardsClient:
    """cards.sillytavern.one API 客户端"""

    def __init__(self, cfg: GlobalConfig):
        self.base_url = cfg.cards_base_url
        self.sso_url = "https://sillytavern.one"
        self.username = cfg.cards_username
        self.password = cfg.cards_password
        self.cookies = None
        self.cookie_file = None

    def login(self, force=False):
        """登录获取 cookies"""
        # 尝试加载已有 cookies
        if not force and self.cookie_file and self.cookie_file.exists():
            with open(self.cookie_file, "r") as f:
                self.cookies = json.load(f)
            # 验证 cookies 是否有效
            if self._check_login():
                print("[cards.sillytavern.one] 使用已有 cookies")
                return

        print("[cards.sillytavern.one] 登录中...")

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })

        # 步骤 1: 访问 cards.sillytavern.one/auth/login
        r = session.get(f"{self.base_url}/auth/login", allow_redirects=True)

        # 步骤 2: 在 sillytavern.one 登录
        if "sillytavern.one" in r.url:
            r = session.post(
                f"{self.sso_url}/login",
                data={"username": self.username, "password": self.password},
                allow_redirects=True
            )

        # 步骤 3: 获取 cards.sillytavern.one session
        r = session.get(f"{self.base_url}/upload")

        # 保存 cookies
        self.cookies = {c.name: c.value for c in session.cookies}

        if self.cookie_file:
            with open(self.cookie_file, "w") as f:
                json.dump(self.cookies, f)

        print(f"  ✓ 登录成功，cookies: {list(self.cookies.keys())}")

    def _check_login(self) -> bool:
        """检查 cookies 是否有效"""
        if not self.cookies:
            return False
        session = requests.Session()
        for name, value in self.cookies.items():
            session.cookies.set(name, value)
        r = session.get(f"{self.base_url}/upload", timeout=10)
        return "登录" not in r.text and "login" not in r.url.lower()

    def upload_card(self, png_path: Path, card_json_path: Path = None) -> dict:
        """
        上传角色卡

        Returns:
            {"success": bool, "id": str, "slug": str, "url": str, "message": str}
        """
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/upload",
        })
        for name, value in self.cookies.items():
            session.cookies.set(name, value)

        # 检查登录状态
        if not self._check_login():
            self.login(force=True)
            for name, value in self.cookies.items():
                session.cookies.set(name, value)

        # 读取卡片数据
        card_name = png_path.stem
        description = ""

        if card_json_path and card_json_path.exists():
            with open(card_json_path, "r", encoding="utf-8") as f:
                v2_card = json.load(f)
            card_name = v2_card.get("data", {}).get("name", card_name)
            description = v2_card.get("data", {}).get("description", "")[:2000]

        # 验证 tEXt chunk
        valid, spec = verify_chara_chunk(str(png_path))
        if valid:
            print(f"  ✓ tEXt chunk 有效 (spec: {spec})")
        else:
            print(f"  ⚠ tEXt chunk 无效，上传可能失败")

        # 构建表单数据
        data = {
            "card_name": card_name,
            "description": description,
            "card_type": "original",
            "author": self.username,
            "has_nsfw_content": "0",
            "has_nsfw_image": "0",
            "orientation": "女性向",
            "cat_genre": ["现代都市", "校园青春"],
            "cat_content": "剧情向",
            "cat_character": "人类",
            "is_public": "1",
        }

        with open(png_path, "rb") as f:
            png_data = f.read()

        files = {"card_file": (png_path.name, png_data, "image/png")}

        # 上传（5 次重试）
        for attempt in range(5):
            try:
                r = session.post(
                    f"{self.base_url}/upload",
                    data=data, files=files,
                    timeout=(90, 300)
                )
                break
            except (TimeoutError, requests.exceptions.Timeout, ProtocolError) as e:
                if attempt < 4:
                    print(f"  ⏳ 重试 ({attempt + 1}/5)...")
                    continue
                raise

        # 提取卡片 ID 和 slug
        card_id = None
        card_slug = None

        thumb_match = re.search(r"/api/card/(\d+)/thumb", r.text)
        if thumb_match:
            card_id = thumb_match.group(1)

        url_match = re.search(r"/card/([^\"']+)", r.url)
        if url_match:
            card_slug = url_match.group(1)

        success = r.status_code == 200 and card_id is not None

        return {
            "success": success,
            "id": card_id,
            "slug": card_slug,
            "url": f"{self.base_url}/card/{card_id}" if card_id else "",
            "message": f"上传成功，ID: {card_id}" if success else f"状态码: {r.status_code}"
        }

    def delete_card(self, card_id: str) -> bool:
        """删除已上传的卡片"""
        session = requests.Session()
        for name, value in self.cookies.items():
            session.cookies.set(name, value)

        r = session.post(f"{self.base_url}/api/card/{card_id}/delete-mine", timeout=30)
        return r.status_code in (200, 404)

    def save_repo_info(self, name: str, card_id: str, slug: str, url: str, output_dir: Path):
        """保存上传元数据"""
        from datetime import datetime
        repo_data = {
            "name": name,
            "id": card_id,
            "slug": slug,
            "url": url,
            "uploaded_at": datetime.now().isoformat(),
        }
        repo_path = output_dir / f"{name}.repo.json"
        with open(repo_path, "w", encoding="utf-8") as f:
            json.dump(repo_data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 已保存 {name}.repo.json")

    def load_repo_info(self, name: str, output_dir: Path) -> dict:
        """读取已有上传元数据"""
        repo_path = output_dir / f"{name}.repo.json"
        if repo_path.exists():
            with open(repo_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


def upload_to_cards(story_name: str = None, card_names: list = None, relogin=False):
    """
    上传角色卡到 cards.sillytavern.one

    Args:
        story_name: 故事名
        card_names: 指定角色名列表（None=全部）
        relogin: 强制重新登录
    """
    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError("未指定故事名")

    output_dir = story.cards_output_dir / "cards_sillytavern_one"
    output_dir.mkdir(parents=True, exist_ok=True)

    client = SillyTavernCardsClient(global_cfg)
    client.cookie_file = story.cards_output_dir / "cookies.json"
    client.login(force=relogin)

    # 确定要上传的角色
    if card_names is None:
        card_names = []
        for f in sorted(os.listdir(output_dir)):
            if f.endswith(".png") and "叙事者" not in f:
                card_names.append(f[:-4])

    print(f"\n准备上传 {len(card_names)} 个角色卡...")

    for card_name in card_names:
        png_path = output_dir / f"{card_name}.png"
        json_path = output_dir / f"{card_name}.json"

        if not png_path.exists():
            print(f"\n❌ 文件不存在: {png_path}")
            continue

        print(f"\n--- 上传: {card_name} ---")

        # 删除旧版本
        old_info = client.load_repo_info(card_name, output_dir)
        if old_info and old_info.get("id"):
            print(f"  📋 删除旧版本: ID={old_info['id']}")
            client.delete_card(old_info["id"])

        # 上传
        result = client.upload_card(png_path, json_path)
        if result["success"]:
            print(f"  ✅ {result['message']}")
            client.save_repo_info(card_name, result["id"], result["slug"], result["url"], output_dir)
        else:
            print(f"  ❌ {result['message']}")

    print("\n完成!")