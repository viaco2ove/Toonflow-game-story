"""
章节更新：解析章节 JSON/MD、上传封面/背景图、保存到服务器

支持两种章节格式:
    1. JSON 格式 (*.json): 直接读取字段
    2. MD 格式 (*.md): 通过 parse_chapter_md 解析

优先级: 同名章节，JSON 优先于 MD
"""
import json
from pathlib import Path

from src.config import GlobalConfig, StoryConfig, load_config
from src.md_parser import parse_chapter_md
from src.toonflow.client import ToonflowClient


def _load_chapter_json(path: Path) -> dict:
    """从 JSON 文件加载章节数据"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_chapter_md(path: Path) -> dict:
    """从 MD 文件解析章节数据"""
    chapter = parse_chapter_md(path)
    return {
        "title": chapter.title,
        "content": chapter.content,
        "backgroundPrompt": chapter.background_prompt,
        "openingRole": chapter.opening_role,
        "openingText": chapter.opening_text,
        "completionCondition": chapter.completion_condition,
    }


def _find_chapter_files(chapters_dir: Path) -> list:
    """
    查找所有章节文件，JSON 优先于 MD

    匹配规则：
    1. 同名 stem（chapter_1.json 覆盖 chapter_1.md）
    2. 数字前缀匹配（chapter_1.json 覆盖 chapter_1_穿越成山大王.md）

    Returns: list of Path
    """
    import re

    json_files = {}
    md_files = {}

    for f in chapters_dir.glob("*.json"):
        name = f.stem
        if name not in ("role.list", "README"):
            json_files[name] = f

    for f in chapters_dir.glob("*.md"):
        name = f.stem
        if name not in ("role.list", "README"):
            md_files[name] = f

    # 收集有哪些 MD 被 JSON 覆盖
    # 规则：JSON 文件名 "chapter_1" 覆盖所有 MD 以 "chapter_1" 开头的文件
    covered_md = set()
    for json_name in json_files:
        # 同名覆盖
        if json_name in md_files:
            covered_md.add(json_name)
        # 数字前缀覆盖：chapter_1.json 覆盖 chapter_1_xxx.md
        m = re.match(r'^(chapter_\d+)$', json_name)
        if m:
            prefix = m.group(1)
            for md_name in md_files:
                if md_name.startswith(prefix) and md_name != prefix:
                    covered_md.add(md_name)

    # 合并：MD 优先放，JSON 覆盖同名/同前缀
    all_files = {}
    for name, f in md_files.items():
        if name not in covered_md:
            all_files[name] = f
    for name, f in json_files.items():
        all_files[name] = f

    # 按文件名排序
    result = []
    for name in sorted(all_files.keys()):
        result.append(all_files[name])

    return result


def update_chapters(client: ToonflowClient, story: StoryConfig, world_data: dict) -> list:
    """
    处理所有章节，返回已保存的章节 ID 列表

    流程:
    1. 获取现有章节（按 sort 序号匹配，防重复创建）
    2. 遍历 chapters/ 目录下的章节文件（JSON 优先于 MD）
    3. 解析章节内容
    4. 上传章节背景图 → 设置 chapter.backgroundPath
       （chapterExtras 封面/背景缩略图由 covers.py 处理）
    5. 保存章节
    """
    if not story.chapters_dir or not story.chapters_dir.exists():
        print("  ⚠ chapters 目录不存在")
        return []

    # 获取现有章节（从 getChapter API 获取原始列表，按 sort 字段排序）
    # 注意：get_chapters 的 dict 有 sort 重复覆盖问题，直接从原始列表取值
    import requests
    API_BASE = ""
    TOKEN = ""
    r_ch = requests.post(f"{API_BASE}/game/getChapter",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"worldId": story.world_id}, timeout=30, verify=False)
    raw_chapters = r_ch.json().get("data", []) or []
    # 按 sort 字段排序，保持服务器返回顺序
    sorted_chapters = sorted(raw_chapters, key=lambda c: c.get("sort", 0))
    # position→chapter（position 从 0 开始）
    existing_by_position = {pos: ch for pos, ch in enumerate(sorted_chapters)}
    existing_by_title = {ch.get("title", ""): ch for ch in raw_chapters}
    existing_by_id = {ch.get("id"): ch for ch in raw_chapters}
    print(f"  现有章节 (position): {list(existing_by_position.keys())}")
    for pos, ch in existing_by_position.items():
        print(f"    position={pos} → id={ch.get('id')} sort={ch.get('sort')} title={ch.get('title','')[:20]}")

    chapter_files = _find_chapter_files(story.chapters_dir)
    saved_ids = []

    for i, chapter_file in enumerate(chapter_files):
        print(f"\n  章节: {chapter_file.name}")

        # 根据文件类型选择加载方式
        if chapter_file.suffix == ".json":
            chapter_data = _load_chapter_json(chapter_file)
            print(f"    (JSON 格式)")
        else:
            chapter_data = _load_chapter_md(chapter_file)
            print(f"    (MD 格式)")

        print(f"    标题: {chapter_data.get('title', '')}")
        print(f"    内容长度: {len(chapter_data.get('content', ''))} 字符")

        # 使用 JSON 中的 sort 字段，或按文件顺序
        sort_index = chapter_data.get("sort", i)
        if "sort" not in chapter_data:
            chapter_data["sort"] = sort_index

        # 上传章节封面图（竖版）→ chapter.coverPath
        # 上传章节背景图（横版）→ chapter.backgroundPath
        # chapterExtras 的 coverPath / background 由 covers.py 处理（但服务器不保存 coverPath）
        chapter_number = sort_index + 1
        if story.chapter_covers:
            cover_info = story.chapter_covers.get(str(chapter_number), {})
            if cover_info.get("cover") and story.image_dir:
                cov_path = story.image_dir / cover_info["cover"]
                if cov_path.exists():
                    uploaded = client.upload_image(cov_path, f"chapter_{chapter_number}_cover", story.project_id)
                    if uploaded:
                        chapter_data["coverPath"] = uploaded
            if cover_info.get("background") and story.image_dir:
                bg_path = story.image_dir / cover_info["background"]
                if bg_path.exists():
                    path = client.upload_image(bg_path, f"chapter_{chapter_number}_bg", story.project_id)
                    if path:
                        chapter_data["backgroundPath"] = path

        # 通过文件顺序 position 匹配现有章节（防重复创建）
        existing = existing_by_position.get(sort_index)
        if not existing:
            # 降级：通过标题匹配
            existing = existing_by_title.get(chapter_data.get("title", ""))

        existing_id = existing.get("id") if existing else None
        if existing_id:
            print(f"    匹配到现有章节 position={sort_index}, id={existing_id}")

        saved = client.save_chapter(chapter_data, story.world_id, existing_id)
        if saved:
            saved_ids.append(saved.get("id"))

    return saved_ids


def get_chapter_entry(client: ToonflowClient, story: StoryConfig, chapter_id: int) -> dict:
    """获取单条章节的完整数据"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    chapter = client.get_chapter_entry(chapter_id)
    if chapter:
        print(f"  ✓ 获取章节: {chapter.get('title', '')} (id={chapter.get('id')})")
        print(f"    排序: {chapter.get('sort')}")
        print(f"    状态: {chapter.get('status')}")
        if content := chapter.get("content"):
            print(f"    内容长度: {len(content)} 字符")
        if background := chapter.get("backgroundPath"):
            print(f"    背景图: {background}")
    else:
        print(f"  ⚠ 未找到章节 id={chapter_id}")
    return chapter


def save_chapter_entry(client: ToonflowClient, story: StoryConfig, entry: dict) -> dict:
    """
    新建或更新单条章节（entry.chapterId/id 有值则更新，无值则新建）

    机制:
    - 传入的 entry 包含章节完整数据（title, content, backgroundPath 等）
    - worldId 自动从 story 配置获取
    - 有 chapterId/id 字段 → 更新现有章节
    - 无 chapterId/id 字段 → 创建新章节
    """
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")

    # 提取章节 ID（有 chapterId 优先，其次 id）
    chapter_id = entry.get("chapterId") or entry.get("id")
    existing_id = chapter_id if chapter_id else None

    # 保存章节
    saved = client.save_chapter(entry, story.world_id, existing_id)

    if saved:
        action = "更新" if existing_id else "新建"
        print(f"  ✓ {action}章节: {saved.get('title', '')} (id={saved.get('id')})")
    return saved


def chapters_op(story_name: str = None, op: str = "list", mode: str = "replace",
                     entry_json: str = None, entry_id: int = None):
    """章节操作入口（供 cli 调用）"""
    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError("未指定故事名，且 .env 中无 CURRENT_STORY")

    print("=" * 60)
    print(f"章节管理: {story.story_name}")
    print(f"环境: {global_cfg.base_url} | World ID: {story.world_id}")
    print(f"操作: {op}")
    print("=" * 60)

    client = ToonflowClient(global_cfg)

    if op == "getChapter":
        if not entry_id:
            raise ValueError("getChapter 操作需要 --entry-id 传章节 id")
        # 返回章节的 json 数据
        get_chapter_entry(client, story, entry_id)
    elif op == "save_create":
        if not entry_json:
            raise ValueError("save_create 操作需要 --entry 传章节 JSON 数据")
        entry = json.loads(entry_json)
        save_chapter_entry(client, story, entry)
    elif op == "save_update":
        if not entry_id:
            raise ValueError("save_update 操作需要 --entry-id 传章节 id")
        if not entry_json:
            raise ValueError("save_update 操作需要 --entry 传章节 JSON 数据")
        entry = json.loads(entry_json)
        # 注入 chapterId 以便更新
        entry["chapterId"] = entry_id
        save_chapter_entry(client, story, entry)
    else:
        raise ValueError(f"未知操作: {op}（支持: getChapter/save_create/save_update）")