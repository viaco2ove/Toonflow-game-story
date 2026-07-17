"""
封面/背景图上传：世界封面、世界封面背景、章节封面/背景

架构说明:
  - 章节级 backgroundPath: 由 chapters.py 上传并设置到 chapter.backgroundPath
  - 世界级 chapterExtras:  由 covers.py 上传封面/背景缩略图到 world.settings.chapterExtras[]
  - 世界封面/背景:         由 covers.py 上传到 world.coverPath / world.settings.coverBgPath
"""
import json
from pathlib import Path

from src.config import StoryConfig
from src.toonflow.client import ToonflowClient


def upload_world_covers(client: ToonflowClient, story: StoryConfig, world_data: dict) -> dict:
    """
    上传世界封面和封面背景图

    在 world settings 中设置:
    - coverPath: 世界封面
    - coverBgPath: 封面背景图
    - chapterExtras[].coverPath / background: 章节封面/背景

    Returns: 更新后的 world_data
    """
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)

    if not story.image_dir or not story.image_dir.exists():
        print("  ⚠ image 目录不存在，跳过封面上传")
        world_data["settings"] = settings
        return world_data

    # 世界封面
    cover_files = list(story.image_dir.glob("story_cover__*.jpg")) + \
                  list(story.image_dir.glob("*_cover.jpg")) + \
                  list(story.image_dir.glob("cover.jpg")) + \
                  list(story.image_dir.glob("cover.png"))
    if cover_files:
        path = client.upload_image(cover_files[0], "world_cover", story.project_id)
        if path:
            settings["coverPath"] = path
            world_data["coverPath"] = path
            print(f"  ✓ 世界封面: {path}")

    # 封面背景图
    cover_bg_files = list(story.image_dir.glob("story_coverBg__*.jpg")) + \
                     list(story.image_dir.glob("*_coverBg.jpg")) + \
                     list(story.image_dir.glob("bg.jpg")) + \
                     list(story.image_dir.glob("bg.png"))
    if cover_bg_files:
        bg_path = client.upload_image(cover_bg_files[0], "world_cover_bg", story.project_id)
        if bg_path:
            settings["coverBgPath"] = bg_path
            print(f"  ✓ 封面背景图: {bg_path}")

    # 章节封面/背景（上传到 chapterExtras）
    if story.chapter_covers:
        chapter_extras = settings.get("chapterExtras", [])
        for idx_str, cover_info in story.chapter_covers.items():
            idx = int(idx_str)
            cover_file = cover_info.get("cover", "")
            bg_file = cover_info.get("background", "")

            uploaded_cover = ""
            uploaded_bg = ""

            if cover_file:
                cover_path = story.image_dir / cover_file
                if cover_path.exists():
                    uploaded_cover = client.upload_image(cover_path, f"chapter_{idx}_cover", story.project_id) or ""

            if bg_file:
                bg_path = story.image_dir / bg_file
                if bg_path.exists():
                    uploaded_bg = client.upload_image(bg_path, f"chapter_{idx}_bg", story.project_id) or ""

            # 查找或创建 chapterExtras 条目
            found = False
            for extra in chapter_extras:
                if extra.get("sort") == idx - 1 or extra.get("chapterId") == idx:
                    if uploaded_cover:
                        extra["coverPath"] = uploaded_cover
                    if uploaded_bg:
                        extra["background"] = uploaded_bg
                    found = True
                    break

            if not found and (uploaded_cover or uploaded_bg):
                chapter_extras.append({
                    "sort": idx - 1,
                    "coverPath": uploaded_cover,
                    "background": uploaded_bg,
                    "music": "",
                    "musicAutoPlay": True,
                    "conditionVisible": True,
                })

        settings["chapterExtras"] = chapter_extras

    world_data["settings"] = settings
    return world_data