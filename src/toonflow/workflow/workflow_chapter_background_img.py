"""
章节封面/背景图上传工作流

【规范】只允许调用 --op 入口函数，不允许直接调用 save_chapter_entry 等内部函数。

流程（走 CLI 入口）:
1. getChapter   → 获取章节完整数据
2. uploadImage  → 上传封面/背景图
3. save_update  → 保存章节更新

用法:
    from src.toonflow.workflow.workflow_chapter_background_img import (
        upload_chapter_images,
        upload_chapter_image,
    )

    # 上传封面和背景
    upload_chapter_images(
        story_name="谁让这个山大王修仙的",
        chapter_id=73,
        cover_path=Path("images/chapter_1_cover.png"),
        background_path=Path("images/chapter_1_bg.png"),
    )

    # 只上传封面
    upload_chapter_image(
        story_name="谁让这个山大王修仙的",
        chapter_id=73,
        image_path=Path("images/chapter_1_cover.png"),
        image_type="cover",
    )

命令行:
    python -m src.cli workflow chapter-background-img \\
        --story 谁让这个山大王修仙的 \\
        --chapter-id 73 \\
        --cover images/chapter_1_cover.png \\
        --background images/chapter_1_bg.png
"""
import json
from pathlib import Path

from src.toonflow.chapters import chapters_op
from src.toonflow.client import client_op


def upload_chapter_image(
    story_name: str,
    image_path: Path,
    project_id: int = 1,
) -> str | None:
    """
    上传单张图片（走 client_op 入口）

    Args:
        story_name: 故事名称（仅用于日志）
        image_path: 图片文件路径
        project_id: 项目 ID

    Returns:
        服务器返回的 filePath，失败返回 None
    """
    if not image_path.exists():
        print(f"  ✗ 文件不存在: {image_path}")
        return None

    print(f"  -> 上传图片: {image_path.name}")
    file_path = client_op(
        op="uploadImage",
        entry_json=str(image_path),
        project_id=project_id,
    )
    return file_path


def upload_chapter_images(
    story_name: str,
    chapter_id: int,
    cover_path: Path = None,
    background_path: Path = None,
    project_id: int = 1,
    save: bool = True,
) -> dict:
    """
    上传章节封面和背景图，并可选保存章节（走 chapters_op / client_op 入口）

    流程:
    1. getChapter  → 获取章节完整数据
    2. uploadImage → 上传封面/背景图（走 client_op）
    3. save_update → 保存章节更新（走 chapters_op）

    Args:
        story_name: 故事名称
        chapter_id: 章节 ID
        cover_path: 封面图路径（可选）
        background_path: 背景图路径（可选）
        project_id: 项目 ID
        save: 是否保存章节到服务器（默认 True）

    Returns:
        包含上传结果的字典 {cover_path, background_path, chapter}
    """
    print("=" * 60)
    print(f"章节图片上传")
    print(f"故事: {story_name}")
    print(f"章节 ID: {chapter_id}")
    print("=" * 60)

    result = {
        "cover_path": None,
        "background_path": None,
        "chapter": None,
    }

    # 1. getChapter - 获取章节完整数据（走 chapters_op 入口）
    print("\n[1/4] 获取章节信息...")
    chapter = chapters_op(story_name=story_name, op="getChapter", entry_id=chapter_id)
    if not chapter:
        raise Exception(f"无法获取章节 {chapter_id}")
    result["chapter"] = chapter
    print(f"  ✓ 获取成功: {chapter.get('title', '')} (id={chapter.get('id')})")

    # 2. uploadImage - 上传封面图（走 client_op 入口）
    if cover_path:
        print("\n[2/4] 上传封面图...")
        cover_path = Path(cover_path)
        if cover_path.exists():
            result["cover_path"] = upload_chapter_image(story_name, cover_path, project_id)
        else:
            print(f"  ⚠ 封面文件不存在: {cover_path}")
    else:
        print("\n[2/4] 跳过封面图（未指定）")

    # 3. uploadImage - 上传背景图（走 client_op 入口）
    if background_path:
        print("\n[3/4] 上传背景图...")
        background_path = Path(background_path)
        if background_path.exists():
            result["background_path"] = upload_chapter_image(story_name, background_path, project_id)
        else:
            print(f"  ⚠ 背景文件不存在: {background_path}")
    else:
        print("\n[3/4] 跳过背景图（未指定）")

    # 4. save_update - 保存章节（走 chapters_op 入口）
    if save and (result["cover_path"] or result["background_path"]):
        print("\n[4/4] 保存章节...")
        # 基于章节完整数据，只更新图片字段
        update_data = dict(chapter)
        update_data["chapterId"] = chapter.get("id") or chapter_id
        update_data["id"] = chapter.get("id") or chapter_id
        # 覆盖图片字段
        if result["background_path"]:
            update_data["backgroundPath"] = result["background_path"]
        if result["cover_path"]:
            update_data["coverPath"] = result["cover_path"]

        saved = chapters_op(
            story_name=story_name,
            op="save_update",
            entry_id=chapter_id,
            entry_json=json.dumps(update_data),
        )
        result["chapter"] = saved
        print(f"  ✓ 章节已保存")
    else:
        print("\n[4/4] 跳过保存（无图片上传或 save=False）")

    print("\n" + "=" * 60)
    print("完成!")
    if result["cover_path"]:
        print(f"  封面: {result['cover_path']}")
    if result["background_path"]:
        print(f"  背景: {result['background_path']}")
    print("=" * 60)

    return result


def workflow_chapter_background_img(
    story_name: str = None,
    chapter_id: int = None,
    cover: str = None,
    background: str = None,
    project_id: int = 1,
):
    """
    CLI 入口：章节封面/背景图上传工作流

    Args:
        story_name: 故事名称
        chapter_id: 章节 ID
        cover: 封面图路径
        background: 背景图路径
        project_id: 项目 ID
    """
    if not chapter_id:
        raise ValueError("需要 --chapter-id 参数")

    cover_path = Path(cover) if cover else None
    background_path = Path(background) if background else None

    if not cover_path and not background_path:
        raise ValueError("需要指定 --cover 或 --background 至少一个")

    return upload_chapter_images(
        story_name=story_name,
        chapter_id=chapter_id,
        cover_path=cover_path,
        background_path=background_path,
        project_id=project_id,
        save=True,
    )
