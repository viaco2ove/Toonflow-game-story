"""
角色立绘一角三图上传工作流

【规范】只允许调用 --op 入口函数，不允许直接调用内部函数。

四角三图字段（按 settings.roles[].xxx 写入）:
- avatarPath           — 人物立绘前景（webp）
- avatarBgPath         — 人物立绘背景（png）
- avatarVideoPath      — 视频文件（mp4）
- avatarFirstFramePath — 首帧图（png）

流程（全部走 CLI 入口）:
1. world_op(get)         → 获取世界完整数据
2. client_op(uploadImage)→ 上传三图（前景 webp / 背景 png / 首帧 png）
3. 修改角色的 avatar* 字段
4. world_op(save)        → 保存世界更新

用法:
    from src.toonflow.workflow.workflow_role_webp_avatar import (
        upload_role_webp_avatar,
    )

    # 上传某个角色的立绘三图
    upload_role_webp_avatar(
        story_name="谁让这个山大王修仙的",
        role_name="陆川",
        webp_path=Path("images/陆川.webp"),
        bg_path=Path("images/陆川_bg.png"),
        first_frame_path=Path("images/陆川_first.png"),
        video_path=Path("images/陆川.mp4"),
        duration_ms=5042,
    )

命令行:
    python -m src.cli workflow role-webp-avatar \\
        --story 谁让这个山大王修仙的 \\
        --role-name 陆川 \\
        --webp images/陆川.webp \\
        --bg images/陆川_bg.png \\
        --first-frame images/陆川_first.png \\
        --video images/陆川.mp4 \\
        --duration-ms 5042
"""
import json
from pathlib import Path

from src.toonflow.client import client_op, world_op


def upload_role_webp_avatar(
    story_name: str,
    role_name: str,
    webp_path: Path = None,
    bg_path: Path = None,
    first_frame_path: Path = None,
    video_path: Path = None,
    duration_ms: int = None,
    project_id: int = 1,
    save: bool = True,
    is_player: bool = False,
) -> dict:
    """
    上传角色立绘一角三图（走 world_op / client_op 入口）

    Args:
        story_name: 故事名称
        role_name: 角色名（按 name 字段匹配）
        webp_path: 前景立绘 webp 路径（设置 avatarPath）
        bg_path: 背景图 png 路径（设置 avatarBgPath）
        first_frame_path: 首帧 png 路径（设置 avatarFirstFramePath）
        video_path: 视频 mp4 路径（设置 avatarVideoPath，仅非玩家角色）
        duration_ms: 视频时长毫秒（设置 avatarDurationMs）
        project_id: 项目 ID
        save: 是否保存到服务器（默认 True）
        is_player: 是否为玩家角色（playerRole 字段，无 avatarVideoPath）

    Returns:
        包含上传结果的字典
    """
    if not any([webp_path, bg_path, first_frame_path, video_path]):
        raise ValueError("至少需要传入一个图片/视频路径")

    print("=" * 60)
    target_label = "玩家角色" if is_player else "角色"
    print(f"{target_label}立绘一角三图上传")
    print(f"故事: {story_name}")
    print(f"{target_label}: {role_name}")
    print("=" * 60)

    result = {
        "role_name": role_name,
        "is_player": is_player,
        "avatar_path": None,
        "avatar_bg_path": None,
        "avatar_video_path": None,
        "avatar_first_frame_path": None,
        "avatar_duration_ms": duration_ms,
        "role": None,
        "world": None,
    }

    # 1. world_op(get) - 获取世界数据
    print("\n[1/5] 获取世界数据...")
    world = world_op(story_name=story_name, op="get")
    if not world:
        raise Exception("无法获取世界数据")
    result["world"] = world
    print(f"  ✓ 世界: {world.get('name')} (id={world.get('id')})")

    # 找到目标对象
    if is_player:
        # 玩家角色在 world.playerRole 顶层
        target = world.get("playerRole")
        if isinstance(target, str):
            target = json.loads(target)
        if not target or target.get("name") != role_name:
            raise ValueError(f"未找到玩家角色: {role_name}（playerRole.name={target.get('name') if target else None}）")
        result["role"] = target
        print(f"  ✓ 找到玩家角色: {role_name} (id={target.get('id')})")
    else:
        # NPC 角色在 settings.roles
        settings = world.get("settings")
        if isinstance(settings, str):
            settings = json.loads(settings)
        roles = (settings or {}).get("roles", [])
        target = None
        for role in roles:
            if role.get("name") == role_name:
                target = role
                break
        if not target:
            raise ValueError(f"未找到角色: {role_name}（world 中现有角色: {[r.get('name') for r in roles]}）")
        result["role"] = target
        print(f"  ✓ 找到角色: {role_name} (id={target.get('id')})")

    # 2-4. client_op(uploadImage) - 上传三图
    print("\n[2/5] 上传立绘前景 (webp)...")
    if webp_path:
        webp_path = Path(webp_path)
        if webp_path.exists():
            result["avatar_path"] = client_op(
                op="uploadImage",
                entry_json=str(webp_path),
                project_id=project_id,
            )
        else:
            print(f"  ⚠ webp 文件不存在: {webp_path}")

    print("\n[3/5] 上传立绘背景 (png)...")
    if bg_path:
        bg_path = Path(bg_path)
        if bg_path.exists():
            result["avatar_bg_path"] = client_op(
                op="uploadImage",
                entry_json=str(bg_path),
                project_id=project_id,
            )
        else:
            print(f"  ⚠ 背景文件不存在: {bg_path}")

    print("\n[4/5] 上传立绘首帧 (png)...")
    if first_frame_path:
        first_frame_path = Path(first_frame_path)
        if first_frame_path.exists():
            result["avatar_first_frame_path"] = client_op(
                op="uploadImage",
                entry_json=str(first_frame_path),
                project_id=project_id,
            )
        else:
            print(f"  ⚠ 首帧文件不存在: {first_frame_path}")

    # 视频通过 uploadImage 同样能上传（玩家角色无此字段，跳过）
    if is_player:
        print("\n[5/5] 玩家角色无 avatarVideoPath 字段，跳过")
    elif video_path:
        print("\n[5/5] 上传视频 (mp4)...")
        video_path = Path(video_path)
        if video_path.exists():
            result["avatar_video_path"] = client_op(
                op="uploadImage",
                entry_json=str(video_path),
                project_id=project_id,
            )
        else:
            print(f"  ⚠ 视频文件不存在: {video_path}")
    else:
        print("\n[5/5] 跳过视频（未指定）")

    # 修改目标对象字段
    if result["avatar_path"]:
        target["avatarPath"] = result["avatar_path"]
    if result["avatar_bg_path"]:
        target["avatarBgPath"] = result["avatar_bg_path"]
    # 玩家角色没有 avatarVideoPath 字段（封面上传.md 实测）
    if result["avatar_video_path"] and not is_player:
        target["avatarVideoPath"] = result["avatar_video_path"]
    if result["avatar_first_frame_path"]:
        target["avatarFirstFramePath"] = result["avatar_first_frame_path"]
    if result["avatar_duration_ms"] is not None:
        target["avatarDurationMs"] = result["avatar_duration_ms"]

    # 5. world_op(save_update) - 保存世界
    if save and any([
        result["avatar_path"],
        result["avatar_bg_path"],
        result["avatar_video_path"],
        result["avatar_first_frame_path"],
    ]):
        print(f"\n保存世界: {role_name} 立绘已更新")

        if is_player:
            # 玩家角色：把 target 写回 world.playerRole（保持 str 形式）
            world["playerRole"] = json.dumps(target, ensure_ascii=False)
        else:
            # NPC 角色：把 settings 序列化写回 world.settings
            world["settings"] = json.dumps(settings, ensure_ascii=False)

        saved = world_op(
            story_name=story_name,
            op="save_update",
            entry_json=json.dumps(world, ensure_ascii=False),
        )
        result["world"] = saved
        print(f"  ✓ {target_label} {role_name} 立绘已绑定到世界")
    else:
        print(f"\n跳过保存（无图片上传或 save=False）")

    print("\n" + "=" * 60)
    print("完成!")
    if result["avatar_path"]:
        print(f"  前景 (webp): {result['avatar_path']}")
    if result["avatar_bg_path"]:
        print(f"  背景 (png):  {result['avatar_bg_path']}")
    if result["avatar_video_path"]:
        print(f"  视频 (mp4):  {result['avatar_video_path']}")
    if result["avatar_first_frame_path"]:
        print(f"  首帧 (png):  {result['avatar_first_frame_path']}")
    print("=" * 60)

    return result


def workflow_role_webp_avatar(
    story_name: str = None,
    role_name: str = None,
    webp: str = None,
    bg: str = None,
    first_frame: str = None,
    video: str = None,
    duration_ms: int = None,
    project_id: int = 1,
    is_player: bool = False,
):
    """
    CLI 入口：角色立绘一角三图上传工作流

    Args:
        story_name: 故事名称
        role_name: 角色名
        webp: 前景 webp 路径
        bg: 背景 png 路径
        first_frame: 首帧 png 路径
        video: 视频 mp4 路径
        duration_ms: 视频时长毫秒
        project_id: 项目 ID
        is_player: 是否为玩家角色（playerRole，无 avatarVideoPath 字段）
    """
    if not role_name:
        raise ValueError("需要 --role-name 参数")

    return upload_role_webp_avatar(
        story_name=story_name,
        role_name=role_name,
        webp_path=Path(webp) if webp else None,
        bg_path=Path(bg) if bg else None,
        first_frame_path=Path(first_frame) if first_frame else None,
        video_path=Path(video) if video else None,
        duration_ms=duration_ms,
        project_id=project_id,
        save=True,
        is_player=is_player,
    )