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

from src.config import GlobalConfig, StoryConfig


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

    def api_call(self, path: str, data: dict, timeout: int = 60) -> dict:
        """调用 API"""
        url = f"{self.base_url}{path}"
        resp = requests.post(
            url, json=data,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=timeout
        )
        return resp.json()

    # ===== 世界管理 =====

    # ---- base64 污染防护（2026-09-06）------------------------------------
    # 服务端 saveWorld 对 settings.roles / playerRole 是 spread 透传
    # （normalizeStoryRole: {...defaults, ...raw}），客户端发来的 base64 大字段
    # 会原样落库。历史脏数据：id=44 单条 settings 103MB（12角色×4个 *Url 字段）。
    # 本地技能走 get_world → 改字段 → save_world 整包写回，若不剥离会把服务端
    # 已有 base64 原样带回，污染循环。故 save_world 前统一剥离。
    _B64_MIN_CHARS = 4096  # 超过此长度且符合 base64 字符集才视为数据块

    _BASE64_CHARS = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\r\n"
    )

    @classmethod
    def _looks_like_base64_blob(cls, value: str) -> bool:
        """判别长 base64 数据块：够长 + 抽样字符集几乎全匹配"""
        if len(value) < cls._B64_MIN_CHARS:
            return False
        sample = value[:2048]
        non_b64 = sum(1 for c in sample if c not in cls._BASE64_CHARS)
        return non_b64 <= len(sample) // 100  # 容忍 1% 噪声

    @classmethod
    def _strip_base64_fields(cls, obj: dict, where: str) -> int:
        """删除 dict 中值为 base64 大块的键，返回删除数"""
        stripped = 0
        if not isinstance(obj, dict):
            return 0
        for key in list(obj.keys()):
            v = obj.get(key)
            if isinstance(v, str) and cls._looks_like_base64_blob(v):
                del obj[key]
                stripped += 1
                print(f"  ⚠ 剥离 base64 字段 {where}.{key} ({len(v):,} chars)")
        return stripped

    @classmethod
    def _sanitize_world_payload(cls, world_data: dict) -> dict:
        """save_world 前剥离 settings.roles / playerRole / narratorRole 内嵌 base64"""
        total = 0
        settings = world_data.get("settings")
        if isinstance(settings, str):
            try:
                parsed = json.loads(settings)
            except (ValueError, TypeError):
                parsed = None
            if isinstance(parsed, dict):
                roles = parsed.get("roles")
                if isinstance(roles, list):
                    for i, role in enumerate(roles):
                        total += cls._strip_base64_fields(
                            role, f"settings.roles[{i}]")
                world_data["settings"] = json.dumps(parsed, ensure_ascii=False)
        elif isinstance(settings, dict):
            roles = settings.get("roles")
            if isinstance(roles, list):
                for i, role in enumerate(roles):
                    total += cls._strip_base64_fields(
                        role, f"settings.roles[{i}]")
        for key in ("playerRole", "narratorRole"):
            role = world_data.get(key)
            if isinstance(role, dict):
                total += cls._strip_base64_fields(role, key)
            elif isinstance(role, str):
                try:
                    parsed = json.loads(role)
                except (ValueError, TypeError):
                    continue
                if isinstance(parsed, dict):
                    n = cls._strip_base64_fields(parsed, key)
                    if n:
                        world_data[key] = json.dumps(parsed, ensure_ascii=False)
                    total += n
        if total:
            print(f"  ✓ 共剥离 {total} 个 base64 大字段（防污染服务端 settings）")
        return world_data

    def get_world(self, world_id: int) -> dict:
        """获取世界数据"""
        result = self.api_call("/game/getWorld", {"worldId": world_id})
        if result.get("code") == 200:
            return result.get("data", {})
        raise Exception(f"获取世界失败: {result}")

    def save_world(self, world_data: dict) -> dict:
        """保存世界数据（自动剥离 role 内嵌 base64 头像字段，防止撑爆服务端 settings）"""
        self._sanitize_world_payload(world_data)
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

    # ===== 世界书 =====

    def list_world_book(self, world_id: int) -> list:
        """列出某世界的全部世界书条目，返回 entry 列表"""
        result = self.api_call("/game/listWorldBook", {"worldId": world_id})
        if result.get("code") == 200:
            return result.get("data", {}).get("entries", [])
        raise Exception(f"获取世界书失败: {result}")

    def save_world_book_entry(self, world_id: int, entry: dict) -> dict:
        """新建或更新世界书条目（entry.id 有值则更新，无值则新建）"""
        result = self.api_call("/game/saveWorldBookEntry", {"worldId": world_id, "entry": entry})
        if result.get("code") == 200:
            return result.get("data", {}).get("entry", {})
        raise Exception(f"保存世界书条目失败: {result}")

    def get_world_book_entry(self, entry_id: int) -> dict:
        """获取单条世界书条目"""
        result = self.api_call("/game/getWorldBookEntry", {"id": entry_id})
        if result.get("code") == 200:
            return result.get("data", {}).get("entry", {})
        raise Exception(f"获取世界书条目失败: {result}")

    def delete_world_book_entry(self, entry_id: int) -> bool:
        """删除世界书条目"""
        result = self.api_call("/game/deleteWorldBookEntry", {"id": entry_id})
        if result.get("code") == 200:
            return True
        raise Exception(f"删除世界书条目失败: {result}")

    def import_world_book(self, world_id: int, entries: list, mode: str = "replace") -> dict:
        """批量导入世界书条目。mode: replace(覆盖) / merge(追加)。返回 {imported, deleted, mode}"""
        result = self.api_call("/game/importWorldBook", {
            "worldId": world_id,
            "entries": entries,
            "mode": mode,
        })
        if result.get("code") == 200:
            return result.get("data", {})
        raise Exception(f"导入世界书失败: {result}")

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
        }, timeout=300)

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

    def get_chapter_entry(self, chapter_id: int) -> dict:
        """获取单条章节数据"""
        result = self.api_call("/game/getChapter", {"chapterId": chapter_id})
        if result.get("code") == 200:
            return result.get("data", {})
        raise Exception(f"获取章节失败: {result}")

    def delete_chapter(self, chapter_id: int, world_id: int) -> bool:
        """删除章节"""
        result = self.api_call("/game/deleteChapter", {"chapterId": chapter_id, "worldId": world_id})
        if result.get("code") == 200:
            print(f"    ✓ 章节删除: ID={chapter_id}")
            return True
        else:
            print(f"    ✗ 章节删除失败: {result}")
            return False

    def get_chapters(self, world_id: int) -> dict:
        """获取世界的章节列表，返回 {sort序号: chapter} 和 {title: chapter} 双索引"""
        chapters = {}
        # 首选: getChapter 只带 worldId 直接返回列表（getWorld 不返回 chapters 字段）
        try:
            resp = self.api_call("/game/getChapter", {"worldId": world_id}, timeout=30)
            if resp.get("code") == 200 and resp.get("data"):
                ch_list = resp.get("data", [])
                for ch in ch_list:
                    if not ch.get("id"):
                        continue
                    raw_sort = ch.get("sort", -1)
                    key = raw_sort - 1 if raw_sort >= 1 else raw_sort
                    chapters[key] = ch
                    chapters[raw_sort] = ch
                    title = ch.get("title", "")
                    if title and title not in chapters:
                        chapters[title] = ch
                return chapters
        except Exception:
            pass
        # 兜底: getWorld → chapters[]
        resp = self.api_call("/game/getWorld", {"worldId": world_id})
        if resp.get("code") == 200:
            data = resp.get("data", {})
            ch_list = data.get("chapters", [])
            if ch_list:
                for ch in ch_list:
                    # 服务器 sort 可能是 1-based，归一化为 0-based
                    raw_sort = ch.get("sort", -1)
                    key = raw_sort - 1 if raw_sort >= 1 else raw_sort
                    chapters[key] = ch
                    chapters[raw_sort] = ch  # 同时保留原始值（兼容）
                    # 同时保留 title 索引（降级匹配）
                    title = ch.get("title", "")
                    if title and title not in chapters:
                        chapters[title] = ch
            else:
                # 按 ID 遍历查找（降级方案）
                for cid in range(1, 200):
                    ch_resp = self.api_call("/game/getChapter", {"chapterId": cid, "worldId": world_id})
                    if ch_resp.get("code") == 200 and ch_resp.get("data"):
                        ch = ch_resp["data"]
                        if ch.get("worldId") == world_id:
                            raw_sort = ch.get("sort", -1)
                            key = raw_sort - 1 if raw_sort >= 1 else raw_sort
                            chapters[key] = ch
                            chapters[raw_sort] = ch
                            title = ch.get("title", "")
                            if title and title not in chapters:
                                chapters[title] = ch
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

    def upload_audio(self, file_path: Path, project_id: int = 1) -> str:
        """上传音频到 voice 服务，返回 filePath（/voice/uploadAudio）"""
        import base64

        if not file_path.exists():
            print(f"    ✗ 文件不存在: {file_path}")
            return None

        with open(file_path, "rb") as f:
            audio_data = f.read()

        ext = file_path.suffix.lower().strip(".")
        if ext == "":
            ext = "wav"
        mime_type = f"audio/{ext}"

        b64_data = f"data:{mime_type};base64,{base64.b64encode(audio_data).decode('utf-8')}"

        print(f"    上传音频: {file_path.name}")
        result = self.api_call("/voice/uploadAudio", {
            "projectId": project_id,
            "base64Data": b64_data,
            "fileName": file_path.name,
        })

        if result.get("code") == 200:
            path = result.get("data", {}).get("filePath")
            print(f"    ✓ 上传成功: {path}")
            return path
        else:
            print(f"    ✗ 上传失败: {result.get('message')}")
            return None


def upload_image(client: ToonflowClient, file_path: Path, project_id: int = 1) -> str:
    """
    上传图片（全局入口函数）

    Args:
        client: ToonflowClient 实例
        file_path: 图片文件路径
        project_id: 项目 ID

    Returns:
        服务器返回的 filePath，失败返回 None
    """
    return client.upload_image(file_path, "scene", project_id)


def upload_audio(client: ToonflowClient, file_path: Path, project_id: int = 1) -> str:
    """
    上传音频（全局入口函数）

    Args:
        client: ToonflowClient 实例
        file_path: 音频文件路径（wav/mp3 等）
        project_id: 项目 ID

    Returns:
        服务器返回的 filePath，失败返回 None
    """
    return client.upload_audio(file_path, project_id)


def get_world_entry(client: ToonflowClient, story: StoryConfig) -> dict:
    """获取世界完整数据（全局入口函数）"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    world = client.get_world(story.world_id)
    print(f"  ✓ 获取世界: {world.get('name')} (id={world.get('id')})")
    return world


def save_world_entry(client: ToonflowClient, story: StoryConfig, world_data: dict) -> dict:
    """保存世界（全局入口函数 — 仅 save_update 路径，禁止无 id 的更新）"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    # 强制校验：禁止无 id 的更新行为
    data_id = world_data.get("id") or world_data.get("worldId")
    if not data_id:
        raise ValueError(
            "禁止无 id 的更新行为！world_data 中必须包含 id 或 worldId 字段，"
            "防止误创建新世界。请用 save_create op 显式创建，或确保数据来自 get_world 返回值。"
        )
    # 注入 worldId 防止丢失
    world_data["id"] = story.world_id
    world_data["worldId"] = story.world_id
    return client.save_world(world_data)


def world_op(story_name: str = None, op: str = "get", entry_json: str = None):
    """
    世界数据操作入口（供 cli 调用）

    op:
      get          - 获取世界完整数据
      save_create  - 新建世界（--entry 传 JSON，id 会被置 0）
      save_update  - 更新现有世界（--entry 传 JSON，必须有 id；禁止无 id 更新）
    """
    from src.config import load_config

    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError("未指定故事名，且 .env 中无 CURRENT_STORY")

    print("=" * 60)
    print(f"世界数据维护: {story.story_name}")
    print(f"环境: {global_cfg.base_url} | World ID: {story.world_id}")
    print(f"操作: {op}")
    print("=" * 60)

    client = ToonflowClient(global_cfg)

    if op == "get":
        return get_world_entry(client, story)
    elif op == "save_create":
        if not entry_json:
            raise ValueError("save_create 操作需要 --entry 传世界 JSON 数据")
        world_data = json.loads(entry_json)
        # 强制 id=0 走新建路径
        world_data["id"] = 0
        world_data["worldId"] = 0
        return client.save_world(world_data)
    elif op == "save_update":
        if not entry_json:
            raise ValueError("save_update 操作需要 --entry 传世界 JSON 数据")
        world_data = json.loads(entry_json)
        # 禁用：禁止无 id 的更新行为（防止误创建新世界）
        if not (world_data.get("id") or world_data.get("worldId")):
            raise ValueError(
                "禁止无 id 的更新行为！请传入包含 id/worldId 的完整 world_data，"
                "或先用 get 操作拉取现有世界数据再修改。"
            )
        return save_world_entry(client, story, world_data)
    else:
        raise ValueError(f"未知操作: {op}（支持: get/save_create/save_update）")


def client_op(story_name: str = None, op: str = "list", mode: str = "replace",
                     entry_json: str = None, entry_id: int = None, world_id: int = None, project_id: int = 1):
    """客户端操作入口（供 cli 调用）"""
    from src.config import load_config

    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError("未指定故事名，且 .env 中无 CURRENT_STORY")

    print("=" * 60)
    print(f"客户端操作")
    print(f"环境: {global_cfg.base_url}")
    print(f"操作: {op}")
    print("=" * 60)

    client = ToonflowClient(global_cfg)

    if op == "uploadImage":
        if not entry_json:
            raise ValueError("uploadImage 操作需要 --entry 传图片文件路径")
        file_path = Path(entry_json)
        if not file_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {file_path}")
        result = upload_image(client, file_path, project_id)
        if result:
            print(f"\n  服务器路径: {result}")
        return result
    elif op == "uploadAudio":
        if not entry_json:
            raise ValueError("uploadAudio 操作需要 --entry 传音色文件路径")
        file_path = Path(entry_json)
        if not file_path.exists():
            raise FileNotFoundError(f"音色文件不存在: {file_path}")
        result = upload_audio(client, file_path, project_id)
        if result:
            print(f"\n  服务器路径: {result}")
        return result
    else:
        raise ValueError(f"未知操作: {op}（支持: uploadImage/uploadAudio）")