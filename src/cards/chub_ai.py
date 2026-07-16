"""
chub.ai 上传客户端

API 流程:
1. GET /authentication/token -> CSRF token
2. POST /authentication/login -> samwise token
3. POST /api/core/characters -> 创建角色
4. PUT /api/core/characters/{username}/{slug} -> 更新角色 + 上传头像
5. PUT /api/project/{id}/metadata -> 上传搜索缩略图
6. DELETE /api/project/{username}/{slug} -> 删除角色
7. POST https://ro.chub.ai/search -> 搜索角色列表
"""
import json
import time
import base64
import os
from pathlib import Path

import requests

from src.config import GlobalConfig, StoryConfig, load_config

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


class ChubAIClient:
    """chub.ai API 客户端"""

    def __init__(self, cfg: GlobalConfig):
        self.username = cfg.chub_username
        self.password = cfg.chub_password
        self.gateway = cfg.chub_gateway
        self.ro_api = cfg.chub_ro_api
        self.samwise = None

    def login(self) -> str:
        """登录获取 samwise token"""
        print("[chub.ai] 获取 CSRF token...")
        resp = requests.get(f"{self.gateway}/authentication/token", headers=HEADERS_COMMON, timeout=30)
        resp.raise_for_status()
        csrf = resp.json()["csrf_token"]

        print("[chub.ai] 登录中...")
        resp = requests.post(
            f"{self.gateway}/authentication/login",
            headers={**HEADERS_COMMON, "content-type": "application/json"},
            json={
                "csrf_token": csrf,
                "email_or_username": self.username,
                "password": self.password,
                "oauth": None, "state": "",
                "redirect_url": "https://chub.ai/login",
                "is_mobile": "false"
            },
            timeout=30
        )
        resp.raise_for_status()
        self.samwise = resp.json()["samwise"]
        print(f"  ✓ 登录成功! samwise: {self.samwise[:20]}...")
        return self.samwise

    def _headers(self, json_content=False) -> dict:
        h = {**HEADERS_COMMON, "ch-api-key": self.samwise, "samwise": self.samwise}
        if json_content:
            h["content-type"] = "application/json"
        return h

    # ===== 角色 CRUD =====

    def create_character(self, v2_card: dict) -> dict:
        """创建新角色，返回 API 响应"""
        data = v2_card.get("data", v2_card)
        payload = self._v2_to_chub_payload(data)
        resp = requests.post(
            f"{self.gateway}/api/core/characters",
            headers=self._headers(json_content=True),
            json=payload, timeout=60
        )
        return resp.json()

    def update_character(self, slug: str, v2_card: dict) -> dict:
        """更新已有角色"""
        data = v2_card.get("data", v2_card)
        payload = self._v2_to_chub_payload(data)
        resp = requests.put(
            f"{self.gateway}/api/core/characters/{self.username}/{slug}",
            headers=self._headers(json_content=True),
            json=payload, timeout=60
        )
        return resp.json()

    def delete_character(self, slug: str) -> bool:
        """删除角色"""
        resp = requests.delete(
            f"{self.gateway}/api/project/{self.username}/{slug}",
            headers=self._headers(), timeout=30
        )
        return resp.status_code in (200, 204)

    def list_characters(self) -> list:
        """列出自己的所有角色"""
        url = (f"{self.ro_api}/search?first=50&namespace=characters&nsfw=true&nsfl=true"
               f"&chub=true&count=false&sort=created_at&username={self.username}"
               f"&only_mine=all&min_tokens=0&page=1&bypass=true")
        resp = requests.post(url, headers=self._headers(json_content=True), json={}, timeout=30)
        data = resp.json()
        return data.get("data", {}).get("nodes", [])

    # ===== 头像上传 =====

    def upload_avatar(self, slug: str, char_id: str, png_path: Path) -> bool:
        """通过 base64 PUT 上传头像"""
        if not png_path.exists():
            print(f"  (无头像 PNG，跳过)")
            return True

        with open(png_path, "rb") as f:
            img_data = f.read()
        b64 = base64.b64encode(img_data).decode("ascii")
        avatar_b64 = f"data:image/png;base64,{b64}"

        headers = self._headers(json_content=True)

        # 完整头像
        url1 = f"{self.gateway}/api/core/characters/{self.username}/{slug}"
        resp1 = requests.put(url1, headers=headers,
                             json={"avatar": avatar_b64, "character_id": int(char_id) if char_id else -1},
                             timeout=60)
        print(f"  头像 PUT core: {resp1.status_code} {'✅' if resp1.status_code == 200 else '❌'}")

        # 搜索缩略图
        if char_id and char_id != "-1":
            url2 = f"{self.gateway}/api/project/{char_id}/metadata"
            resp2 = requests.put(url2, headers=headers, json={"avatar": avatar_b64}, timeout=60)
            print(f"  头像 PUT meta: {resp2.status_code} {'✅' if resp2.status_code == 200 else '❌'}")
            return resp1.status_code == 200

        return resp1.status_code == 200

    # ===== 仓库元数据 =====

    def save_repo_info(self, name: str, char_id: str, slug: str, output_dir: Path):
        """保存上传元数据到 .repo.chub_ai.json"""
        repo_data = {
            "name": name,
            "id": str(char_id),
            "slug": slug,
            "url": f"https://chub.ai/characters/{self.username}/{slug}" if slug else "",
            "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        repo_path = output_dir / f"{name}.repo.chub_ai.json"
        with open(repo_path, "w", encoding="utf-8") as f:
            json.dump(repo_data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 已保存 {name}.repo.chub_ai.json")

    def load_repo_info(self, name: str, output_dir: Path) -> dict:
        """读取已有上传元数据"""
        repo_path = output_dir / f"{name}.repo.chub_ai.json"
        if repo_path.exists():
            with open(repo_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    # ===== 内部方法 =====

    def _v2_to_chub_payload(self, data: dict) -> dict:
        """将 V2 角色卡格式转换为 chub.ai API payload"""
        return {
            "name": data.get("name", ""),
            "avatar": "",
            "tagline": (data.get("description", "") or "")[:100],
            "in_chat_name": data.get("name", ""),
            "description": data.get("description", ""),
            "tags": data.get("tags", ["Roleplay"]) or ["Roleplay"],
            "is_public": True,
            "is_nsfw": False,
            "is_anonymous": False,
            "personality": data.get("personality", ""),
            "first_message": data.get("first_mes", data.get("first_message", "")),
            "scenario": data.get("scenario", ""),
            "example_dialogs": data.get("mes_example", ""),
            "voice_id": None,
            "alternate_greetings": data.get("alternate_greetings", []) or [],
            "system_prompt": "",
            "post_history_instructions": "",
            "depth_prompt": {"depth": 0, "prompt": ""},
            "embedded_lorebook": None,
            "is_unlisted": False,
            "extensions": {"depth_prompt": {"depth": 0, "prompt": ""}},
            "character_book": None,
            "character_id": -1,
        }


def upload_to_chub(story_name: str = None, card_names: list = None, avatar_only: bool = False):
    """
    上传角色卡到 chub.ai

    Args:
        story_name: 故事名
        card_names: 指定角色名列表（None=全部）
        avatar_only: 只上传头像
    """
    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError("未指定故事名")

    output_dir = story.cards_output_dir / "chub_ai"
    output_dir.mkdir(parents=True, exist_ok=True)

    client = ChubAIClient(global_cfg)
    client.login()

    # 确定要处理的角色
    if card_names is None:
        # 自动列出所有角色 JSON（排除非角色文件）
        card_names = []
        for f in sorted(os.listdir(output_dir)):
            if f.endswith(".json") and ".repo" not in f and not f.startswith(("INDEX", "世界书", "旁白")):
                card_names.append(f[:-5])

    if avatar_only:
        # 只上传头像
        print(f"\n只上传头像，共 {len(card_names)} 个角色\n")
        for i, name in enumerate(card_names, 1):
            repo = client.load_repo_info(name, output_dir)
            if not repo or not repo.get("slug"):
                print(f"[{i}/{len(card_names)}] {name}: 无 repo 文件，跳过")
                continue
            png_path = output_dir / f"{name}.png"
            # 降级到故事 avatars 目录
            if not png_path.exists():
                for role in ([story.player_role] if story.player_role else []) + story.npc_roles:
                    if role and role.name == name and role.avatar_file:
                        png_path = story.avatars_dir / role.avatar_file
                        break
            print(f"[{i}/{len(card_names)}] 上传头像: {name}")
            client.upload_avatar(repo["slug"], repo.get("id", ""), png_path)
            print()
            time.sleep(1)
    else:
        # 上传角色 + 头像
        print(f"\n上传角色+头像，共 {len(card_names)} 个角色: {card_names}")

        for i, name in enumerate(card_names, 1):
            print(f"\n[{i}/{len(card_names)}] 处理: {name}")

            json_path = output_dir / f"{name}.json"
            if not json_path.exists():
                print(f"  ⚠ 角色卡 JSON 不存在: {json_path}")
                continue

            with open(json_path, "r", encoding="utf-8") as f:
                v2_card = json.load(f)

            # 检查是否已存在
            repo = client.load_repo_info(name, output_dir)
            existing_slug = repo.get("slug", "") if repo else ""

            if existing_slug:
                # 更新
                print(f"  更新: {existing_slug}")
                result = client.update_character(existing_slug, v2_card)
            else:
                # 新建
                print(f"  创建新角色...")
                result = client.create_character(v2_card)

            slug = result.get("path_with_namespace", "").split("/")[-1] or existing_slug
            char_id = str(result.get("id", ""))

            if slug:
                client.save_repo_info(name, char_id, slug, output_dir)
                print(f"  ✅ https://chub.ai/characters/{client.username}/{slug}")

                # 上传头像
                png_path = output_dir / f"{name}.png"
                # 降级到故事 avatars 目录
                if not png_path.exists():
                    for role in ([story.player_role] if story.player_role else []) + story.npc_roles:
                        if role and role.name == name and role.avatar_file:
                            png_path = story.avatars_dir / role.avatar_file
                            break
                if png_path.exists():
                    client.upload_avatar(slug, char_id, png_path)
            else:
                print(f"  ❌ 上传失败: {result}")

            time.sleep(2)

    print("\n全部完成!")