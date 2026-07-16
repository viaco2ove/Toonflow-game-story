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

    Returns: list of (Path, sort_index)
    """
    # 收集所有章节文件
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

    # 合并：JSON 优先
    all_files = {}
    for name, f in md_files.items():
        all_files[name] = f
    for name, f in json_files.items():
        all_files[name] = f  # JSON 覆盖同名的 MD

    # 按文件名排序
    result = []
    for name in sorted(all_files.keys()):
        result.append(all_files[name])

    return result


def update_chapters(client: ToonflowClient, story: StoryConfig, world_data: dict) -> list:
    """
    处理所有章节，返回已保存的章节 ID 列表

    流程:
    1. 获取现有章节（按标题匹配）
    2. 遍历 chapters/ 目录下的章节文件（JSON 优先于 MD）
    3. 解析章节内容
    4. 上传封面/背景图（如有）
    5. 保存章节
    """
    if not story.chapters_dir or not story.chapters_dir.exists():
        print("  ⚠ chapters 目录不存在")
        return []

    # 获取现有章节
    existing_chapters = client.get_chapters(story.world_id)
    print(f"  现有章节: {list(existing_chapters.keys())}")

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
        if "sort" not in chapter_data:
            chapter_data["sort"] = i

        # 上传章节封面和背景图
        chapter_index = chapter_data.get("sort", i) + 1
        if story.chapter_covers:
            cover_info = story.chapter_covers.get(str(chapter_index), {})
            if cover_info.get("cover") and story.image_dir:
                cover_path = story.image_dir / cover_info["cover"]
                if cover_path.exists():
                    path = client.upload_image(cover_path, f"chapter_{chapter_index}_cover", story.project_id)
                    if path:
                        chapter_data["coverPath"] = path
            if cover_info.get("background") and story.image_dir:
                bg_path = story.image_dir / cover_info["background"]
                if bg_path.exists():
                    path = client.upload_image(bg_path, f"chapter_{chapter_index}_bg", story.project_id)
                    if path:
                        chapter_data["backgroundPath"] = path

        # 通过标题匹配现有章节
        existing = existing_chapters.get(chapter_data.get("title", ""))
        existing_id = existing.get("id") if existing else None

        saved = client.save_chapter(chapter_data, story.world_id, existing_id)
        if saved:
            saved_ids.append(saved.get("id"))

    return saved_ids