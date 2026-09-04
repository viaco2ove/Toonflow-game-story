"""
Toonflow → agme_cache 下载器

将服务端世界的完整数据拉取到本地 toonflow_agme_cache/ 目录，
完全模仿「谁让这个山大王修仙的/toonflow_agme_cache」的结构。

用法:
    python -m src.cli agme_cache --story "故事名"
    python -m src.cli agme_cache --story "故事名" --world-id 44

输出目录:
    {story_dir}/toonflow_agme_cache/
    ├── avatars/{name}/
    │   ├── original.png     # 本地原始图（从 avatars/ 目录）
    │   ├── avatar.webp      # 服务端抠图头像（下载）
    │   ├── background.png   # 服务端抠图背景（下载）
    │   ├── role.json        # 服务端角色完整数据
    │   └── voice.wav        # 服务端生成的音色（下载）
    ├── chapters/
    │   ├── backgrounds/
    │   │   ├── chapter_1.png
    │   │   └── chapter_2.png
    │   ├── chapter_1.json
    │   ├── chapter_1_{title}.md   # content 转为 Markdown
    │   ├── chapter_2.json
    │   └── chapter_2_{title}.md
    └── images/
        └── world_cover.jpg
"""

import json
import re
import sys
import base64
import requests
from pathlib import Path
from urllib.parse import urlparse

# 避免循环导入：只从 toonflow 导入 Client
from src.toonflow.client import ToonflowClient
from src.config import load_global_config, load_story_config


BASE_URL_FILE = "http://10.10.2.195:60002"


def _resolve_file_url(file_path: str) -> str:
    """
    将服务端文件路径转为可下载的 HTTP URL。
    路径格式示例: /1/game/role/xxx.webp
    """
    if not file_path:
        return ""
    if file_path.startswith("http"):
        return file_path
    return f"{BASE_URL_FILE}{file_path}"


def _rebase_url(url: str, base_url: str) -> str:
    """
    把绝对 URL 的 host 重写为当前配置的服务器。
    服务端数据库里存的文件 URL 可能带旧 IP（如 10.10.2.195）或 127.0.0.1，
    换服务器后这些 host 不可达，统一换成 .env 里的 BASE_URL host。
    """
    if not url:
        return url
    parsed = urlparse(url)
    # 已是目标 host，直接返回
    target = urlparse(base_url)
    if parsed.netloc == target.netloc:
        return url
    return f"{target.scheme}://{target.netloc}{parsed.path}" + (f"?{parsed.query}" if parsed.query else "")


def _download_bytes(url: str, token: str, timeout: int = 60) -> bytes:
    """下载文件内容（bytes），失败返回 None"""
    if not url:
        return None
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=timeout)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        pass
    return None


def _download_and_save(url: str, token: str, save_path: Path, timeout: int = 60) -> bool:
    """下载文件并保存到本地，失败打印警告但不抛异常"""
    data = _download_bytes(url, token, timeout)
    if data is None:
        print(f"    ⚠ 下载失败: {url}")
        return False
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(data)
    print(f"    ✓ {save_path.name} ({len(data):,} bytes)")
    return True


def _content_to_md(content: str) -> str:
    """
    将 chapter.content 格式转为 Markdown。
    输入格式: # 标题\n\n## 大节\n### 小节\n@角色：台词\n### 用户发言\n\n...
    输出: 直接可读的 Markdown
    """
    if not content:
        return ""
    # content 本身已经是 Markdown 格式，只做最小清理
    text = content.strip()
    # 清理可能的尾部多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def pull_agme_cache(story_name: str, world_id: int = None, project_id: int = 1):
    """
    主函数：拉取服务端数据到本地 agme_cache 目录
    """
    # 1. 加载配置
    global_cfg = load_global_config()
    if story_name:
        story_cfg = load_story_config(story_name, global_cfg)
    else:
        story_cfg = None

    if world_id is None and story_cfg:
        world_id = story_cfg.world_id
    if world_id is None:
        raise ValueError("必须指定 world_id（通过 --world-id 或 story.json 中的 world_id）")

    try:
        client = ToonflowClient(global_cfg)
    except requests.exceptions.ConnectTimeoutError as e:
        raise ConnectionError(
            f"无法连接到 Toonflow 服务器 ({global_cfg.base_url})，"
            "请确认：\n"
            "  1. 服务器在本机网络可达（ping 服务器 IP）\n"
            "  2. 服务已启动（端口 60002）\n"
            "  3. BASE_URL 与实际部署地址一致"
        ) from e
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(
            f"连接 Toonflow 服务器失败: {e}\n"
            "检查服务器地址和端口是否正确。"
        ) from e
    token = client.token
    base_url = global_cfg.base_url.rstrip("/")

    # 2. 拉取世界数据
    print(f"\n{'='*60}")
    print(f"拉取世界数据: world_id={world_id}")
    print(f"{'='*60}")
    world = client.get_world(world_id)

    story_title = world.get("name", story_name or "未知故事")
    story_dir = story_cfg.story_dir if story_cfg else Path(global_cfg.project_root) / "ai_story" / "unknown"
    cache_dir = story_dir / "toonflow_agme_cache"

    print(f"  故事名: {story_title}")
    print(f"  缓存目录: {cache_dir}")

    # 3. 解析 settings
    settings_raw = world.get("settings", "{}")
    if isinstance(settings_raw, str):
        settings = json.loads(settings_raw)
    else:
        settings = settings_raw or {}

    roles_in_settings = settings.get("roles", [])
    player_role = world.get("playerRole", {})
    narrator_role = world.get("narratorRole", {})

    # 4. 下载世界封面
    print(f"\n{'='*60}")
    print("下载世界封面")
    print(f"{'='*60}")
    images_dir = cache_dir / "images"
    cover_path = world.get("coverPath", "")
    if cover_path:
        cover_url = _rebase_url(_resolve_file_url(cover_path), base_url)
        _download_and_save(cover_url, token, images_dir / "world_cover.jpg")
    else:
        # 尝试从 local image/ 目录找 cover.png
        local_cover = story_dir / "image" / "cover.png"
        if local_cover.exists():
            import shutil
            shutil.copy(local_cover, images_dir / "world_cover.jpg")
            print(f"    ✓ 复制本地封面: world_cover.jpg")

    # 5. 下载角色数据
    print(f"\n{'='*60}")
    print(f"下载角色数据 ({len(roles_in_settings)} NPC + player + narrator)")
    print(f"{'='*60}")

    # 本地头像目录
    local_avatars_dir = story_dir / "avatars"

    all_roles = []
    if player_role:
        all_roles.append(("player", player_role))
    if narrator_role:
        all_roles.append(("narrator", narrator_role))
    for r in roles_in_settings:
        all_roles.append((r.get("name", "unknown"), r))

    # 用于 role.json 的精简数据（与样例一致）
    for role_name, role_data in all_roles:
        role_dir = cache_dir / "avatars" / role_name
        role_dir.mkdir(parents=True, exist_ok=True)

        # role.json：服务端完整数据（字段与样例一致）
        role_json_path = role_dir / "role.json"
        with open(role_json_path, "w", encoding="utf-8") as f:
            json.dump(role_data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ {role_name}/role.json ({len(json.dumps(role_data, ensure_ascii=False)):,} bytes)")

        role_type = role_data.get("roleType", "")

        # original.png: 从本地 avatars/ 目录匹配
        if role_type != "narrator":
            # 尝试多种文件名匹配
            possible_names = [role_name]
            if role_name == "用户":
                possible_names = ["用户", "陈曦"]
            for local_name in possible_names:
                for ext in ["png", "jpg", "webp"]:
                    local_path = local_avatars_dir / f"{local_name}.{ext}"
                    if local_path.exists():
                        import shutil
                        shutil.copy(local_path, role_dir / f"original.{ext}")
                        print(f"  ✓ {role_name}/original.{ext} (本地复制)")
                        break
                else:
                    continue
                break

        # avatar.webp + background.png: 从服务端下载
        avatar_path = role_data.get("avatarPath", "")
        avatar_bg_path = role_data.get("avatarBgPath", "")

        if avatar_path:
            url = _rebase_url(_resolve_file_url(avatar_path), base_url)
            ext = Path(urlparse(url).path).suffix or ".webp"
            _download_and_save(url, token, role_dir / f"avatar{ext}")

        if avatar_bg_path:
            url = _rebase_url(_resolve_file_url(avatar_bg_path), base_url)
            ext = Path(urlparse(url).path).suffix or ".png"
            _download_and_save(url, token, role_dir / f"background{ext}")

        # voice.wav: 从服务端下载（URL 可能指向 127.0.0.1，重写 host）
        voice_url = role_data.get("voiceGeneratedDownloadUrl", "")
        if voice_url:
            _download_and_save(_rebase_url(voice_url, base_url), token, role_dir / "voice.wav", timeout=120)

    # 6. 下载章节数据
    print(f"\n{'='*60}")
    print("下载章节数据")
    print(f"{'='*60}")

    chapters = client.get_chapters(world_id)
    # chapters 是 {sort: chapter, title: chapter, ...} 字典
    # 去重：用 id 做主键
    chapters_by_id = {}
    for ch in chapters.values():
        cid = ch.get("id")
        if cid and cid not in chapters_by_id:
            chapters_by_id[cid] = ch

    if not chapters_by_id:
        print("  ⚠ 服务端无章节数据，跳过")

    backgrounds_dir = cache_dir / "chapters" / "backgrounds"
    backgrounds_dir.mkdir(parents=True, exist_ok=True)

    # 按 sort 排序
    sorted_chapters = sorted(chapters_by_id.values(), key=lambda c: c.get("sort", 0))

    for idx, ch in enumerate(sorted_chapters):
        cid = ch.get("id")
        title = ch.get("title", f"chapter_{cid}")
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        # 用序号编号（服务端 sort 可能重复，会导致文件名覆盖）
        sort = idx + 1

        print(f"\n  章节 {idx+1}: {title} (ID={cid})")

        # chapter_X.json（服务端原始数据）
        ch_json_path = cache_dir / "chapters" / f"chapter_{sort}.json"
        with open(ch_json_path, "w", encoding="utf-8") as f:
            json.dump(ch, f, ensure_ascii=False, indent=2)
        print(f"    ✓ chapter_{sort}.json")

        # chapter_X_{title}.md（content 转为 Markdown）
        content = ch.get("content", "")
        md_content = _content_to_md(content)
        if md_content:
            md_path = cache_dir / "chapters" / f"chapter_{sort}_{safe_title}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"    ✓ chapter_{sort}_{safe_title}.md")

        # chapter background
        bg_path = ch.get("backgroundPath", "")
        if bg_path:
            url = _rebase_url(_resolve_file_url(bg_path), base_url)
            _download_and_save(url, token, backgrounds_dir / f"chapter_{sort}.png")

    print(f"\n{'='*60}")
    print(f"✅ 拉取完成: {story_title}")
    print(f"   缓存目录: {cache_dir}")
    print(f"   角色: {len(all_roles)} 个")
    print(f"   章节: {len(sorted_chapters)} 个")
    print(f"{'='*60}")

    # 7. 写 metadata.json（方便后续 skill 读取）
    meta = {
        "world_id": world_id,
        "story_name": story_title,
        "world_cover_url": _resolve_file_url(cover_path),
        "roles_count": len(all_roles),
        "chapters_count": len(sorted_chapters),
        "pulled_at": __import__("datetime").datetime.now().isoformat(),
    }
    meta_path = cache_dir / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  ✓ metadata.json")


# =============================================================================
# CLI 入口（由 src/cli.py 路由）
# =============================================================================

def cmd_agme_cache_pull(args):
    """CLI: python -m src.cli agme_cache --story "xxx" [--world-id N]"""
    pull_agme_cache(
        story_name=args.story or None,
        world_id=int(args.world_id) if args.world_id else None,
        project_id=int(args.project_id) if args.project_id else 1,
    )
