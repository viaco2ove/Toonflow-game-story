"""
Toonflow API 客户端：登录、世界管理、角色、章节、图片上传

API 调用模式:
    POST {BASE_URL}{path}
    Headers: Authorization: Bearer {TOKEN}
    Body: JSON
    Response: {"code": 200, "data": {...}, "message": ""}
"""
import json
import requests
from pathlib import Path

from src.config import GlobalConfig


class ToonflowClient:
    """Toonflow 服务器 API 客户端"""

    def __init__(self, cfg: GlobalConfig):
        self.base_url = cfg.base_url.rstrip("/")
        self.token = cfg.token
        self.username = cfg.username
        self.password = cfg.password
        self._ensure_token()

    def _ensure_token(self):
        """确保 TOKEN 有效，无效则重新登录"""
        if self.token:
            # 测试 token
            try:
                resp = requests.post(
                    f"{self.base_url}/game/getWorld",
                    json={"worldId": 1},
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=10
                )
                if resp.status_code != 401 and "无效的token" not in resp.text:
                    return
            except Exception:
                pass

        # 重新登录
        print("  -> Token 无效，正在重新登录...")
        resp = requests.post(
            f"{self.base_url}/other/login",
            json={"username": self.username, "password": self.password},
            timeout=10
        )
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 200:
                self.token = result["data"]["token"].replace("Bearer ", "").replace("bearer ", "")
                # 更新全局 .env 中的 TOKEN
                self._save_token()
                print(f"  ✓ 新 Token 已保存")
                return

        raise Exception(f"登录失败: {resp.text}")

    def _save_token(self):
        """保存 token 到全局 .env"""
        from src.config import _parse_env_file
        env_path = Path(__file__).parent.parent / ".env"
        if not env_path.exists():
            return

        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith("TOKEN="):
                new_lines.append(f"TOKEN={self.token}\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"TOKEN={self.token}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def api_call(self, path: str, data: dict) -> dict:
        """调用 API"""
        url = f"{self.base_url}{path}"
        resp = requests.post(
            url, json=data,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=60
        )
        return resp.json()

    # ===== 世界管理 =====

    def get_world(self, world_id: int) -> dict:
        """获取世界数据"""
        result = self.api_call("/game/getWorld", {"worldId": world_id})
        if result.get("code") == 200:
            return result.get("data", {})
        raise Exception(f"获取世界失败: {result}")

    def save_world(self, world_data: dict) -> dict:
        """保存世界数据"""
        result = self.api_call("/game/saveWorld", world_data)
        if result.get("code") == 200:
            print("  ✓ 世界保存成功")
            return result.get("data", {})
        else:
            print(f"  ✗ 世界保存失败: {result}")
            return None

    def create_world(self, project_id: int, name: str, intro: str, global_bg: str) -> dict:
        """创建新世界"""
        world_data = {
            "projectId": project_id,
            "name": name,
            "intro": intro,
            "worldId": 0,
            "settings": json.dumps({
                "roles": [],
                "globalBackground": global_bg
            })
        }
        result = self.api_call("/game/saveWorld", world_data)
        if result.get("code") == 200:
            return result.get("data", {})
        raise Exception(f"创建世界失败: {result}")

    # ===== 角色 =====

    def separate_avatar(self, avatar_path: Path, role_name: str, world_id: int) -> dict:
        """上传头像并进行人体分离"""
        import base64

        print(f"    -> 分离头像: {avatar_path.name}")

        with open(avatar_path, "rb") as f:
            img_data = f.read()
        b64_data = base64.b64encode(img_data).decode("utf-8")

        result = self.api_call("/game/separateRoleAvatar", {
            "worldId": world_id,
            "base64Data": b64_data,
            "roleName": role_name
        })

        if result.get("code") == 200:
            data = result.get("data", {})
            return {
                "avatarSourcePath": data.get("sourceFilePath", ""),
                "avatarPath": data.get("foregroundFilePath", ""),
                "avatarBgPath": data.get("backgroundFilePath", ""),
            }
        else:
            print(f"    ✗ 分离失败: {result.get('message', str(result))}")
            return {}

    # ===== 章节 =====

    def save_chapter(self, chapter_data: dict, world_id: int, existing_id: int = None) -> dict:
        """保存章节（存在则更新，否则创建）"""
        chapter_data["worldId"] = world_id
        chapter_data["status"] = "draft"
        if existing_id:
            chapter_data["chapterId"] = existing_id
            chapter_data["id"] = existing_id

        result = self.api_call("/game/saveChapter", chapter_data)
        if result.get("code") == 200:
            ch_id = result.get("data", {}).get("id")
            action = "更新" if existing_id else "创建"
            print(f"    ✓ 章节{action}: {chapter_data.get('title', '')} (ID={ch_id})")
            return result.get("data", {})
        else:
            print(f"    ✗ 章节保存失败: {result}")
            return None

    def get_chapters(self, world_id: int) -> dict:
        """获取世界的章节列表（按标题索引）"""
        resp = self.api_call("/game/getWorld", {"worldId": world_id})
        chapters = {}
        if resp.get("code") == 200:
            data = resp.get("data", {})
            ch_list = data.get("chapters", [])
            if ch_list:
                chapters = {ch.get("title", ""): ch for ch in ch_list}
            else:
                # 按 ID 遍历查找
                for cid in range(1, 200):
                    ch_resp = self.api_call("/game/getChapter", {"chapterId": cid, "worldId": world_id})
                    if ch_resp.get("code") == 200 and ch_resp.get("data"):
                        ch = ch_resp["data"]
                        if ch.get("worldId") == world_id:
                            chapters[ch.get("title", "")] = ch
        return chapters

    # ===== 图片上传 =====

    def upload_image(self, file_path: Path, image_type: str = "scene", project_id: int = 1) -> str:
        """上传图片到服务器，返回 filePath"""
        import base64

        if not file_path.exists():
            print(f"    ✗ 文件不存在: {file_path}")
            return None

        with open(file_path, "rb") as f:
            image_data = f.read()

        ext = file_path.suffix.lower().strip(".")
        if ext == "jpeg":
            ext = "jpg"
        mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        b64_data = f"data:{mime_type};base64,{base64.b64encode(image_data).decode('utf-8')}"

        print(f"    上传: {file_path.name}")
        result = self.api_call("/game/uploadImage", {
            "projectId": project_id,
            "type": "scene",
            "fileName": f"{image_type}_{file_path.stem}.{ext}",
            "base64Data": b64_data
        })

        if result.get("code") == 200:
            path = result.get("data", {}).get("filePath")
            print(f"    ✓ 上传成功: {path}")
            return path
        else:
            print(f"    ✗ 上传失败: {result.get('message')}")
            return None