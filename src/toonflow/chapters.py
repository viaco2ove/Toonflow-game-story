"""
章节更新：解析章节 MD、上传封面/背景图、保存到服务器
"""
import json
from pathlib import Path

from src.config import StoryConfig
from src.md_parser import parse_chapter_md
from src.toonflow.client import ToonflowClient


def update_chapters(client: ToonflowClient, story: StoryConfig, world_data: dict) -> list:
    """
    处理所有章节，返回已保存的章节 ID 列表

    流程:
    1. 获取现有章节（按标题匹配）
    2. 遍历 chapters/ 目录下的 chapter_*.md
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

    chapter_files = sorted(story.chapters_dir.glob("*.md"))
    # 过滤非章节文件
    chapter_files = [f for f in chapter_files if f.stem not in ("role.list", "README")]

    saved_ids = []

    for i, chapter_file in enumerate(chapter_files):
        print(f"\n  章节: {chapter_file.name}")
        chapter = parse_chapter_md(chapter_file)
        print(f"    标题: {chapter.title}")
        print(f"    内容长度: {len(chapter.content)} 字符")

        chapter_data = {
            "title": chapter.title,
            "content": chapter.content,
            "backgroundPrompt": chapter.background_prompt,
            "openingRole": chapter.opening_role,
            "openingText": chapter.opening_text,
            "completionCondition": chapter.completion_condition,
            "sort": i,
        }

        # 上传章节封面和背景图
        if story.chapter_covers:
            cover_info = story.chapter_covers.get(str(i + 1), {})
            if cover_info.get("cover") and story.image_dir:
                cover_path = story.image_dir / cover_info["cover"]
                if cover_path.exists():
                    path = client.upload_image(cover_path, f"chapter_{i+1}_cover", story.project_id)
                    if path:
                        chapter_data["coverPath"] = path
            if cover_info.get("background") and story.image_dir:
                bg_path = story.image_dir / cover_info["background"]
                if bg_path.exists():
                    path = client.upload_image(bg_path, f"chapter_{i+1}_bg", story.project_id)
                    if path:
                        chapter_data["backgroundPath"] = path

        # 通过标题匹配现有章节
        existing = existing_chapters.get(chapter.title)
        existing_id = existing.get("id") if existing else None

        saved = client.save_chapter(chapter_data, story.world_id, existing_id)
        if saved:
            saved_ids.append(saved.get("id"))

    return saved_ids