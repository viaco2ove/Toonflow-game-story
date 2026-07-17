"""
章节更新：解析章节 JSON/MD、上传封面/背景图、保存到服务器

支持两种章节格式:
    1. JSON 格式 (*.json): 直接读取字段
    2. MD 格式 (*.md): 通过 parse_chapter_md 解析

优先级: 同名章节，JSON 优先于 MD
"""
import json
from pathlib import Path

from src.config import StoryConfig
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

    # 获取现有章节（按 sort 序号索引）
    existing_chapters = client.get_chapters(story.world_id)
    existing_by_sort = {}
    existing_by_title = {}
    for key, ch in existing_chapters.items():
        if isinstance(key, int) and key >= 0:
            existing_by_sort[key] = ch
        else:
            existing_by_title[key] = ch
    print(f"  现有章节 (sort): {list(existing_by_sort.keys())}")
    if existing_by_title:
        print(f"  现有章节 (title): {list(existing_by_title.keys())}")

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

        # 上传章节背景图，设置到 chapter.backgroundPath
        # （chapterExtras 封面/背景缩略图由 covers.py 处理）
        chapter_number = sort_index + 1
        if story.chapter_covers:
            cover_info = story.chapter_covers.get(str(chapter_number), {})
            if cover_info.get("background") and story.image_dir:
                bg_path = story.image_dir / cover_info["background"]
                if bg_path.exists():
                    path = client.upload_image(bg_path, f"chapter_{chapter_number}_bg", story.project_id)
                    if path:
                        chapter_data["backgroundPath"] = path

        # 通过 sort 序号匹配现有章节（防重复创建）
        existing = existing_by_sort.get(sort_index)
        if not existing:
            # 降级：通过标题匹配
            existing = existing_by_title.get(chapter_data.get("title", ""))

        existing_id = existing.get("id") if existing else None
        if existing_id:
            print(f"    匹配到现有章节 sort={sort_index}, id={existing_id}")

        saved = client.save_chapter(chapter_data, story.world_id, existing_id)
        if saved:
            saved_ids.append(saved.get("id"))

    return saved_ids