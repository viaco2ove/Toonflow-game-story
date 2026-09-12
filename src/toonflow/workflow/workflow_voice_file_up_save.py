"""
角色音色文件上传并绑定到故事工作流

【规范】只允许调用 --op 入口函数，不允许直接调用内部函数。

流程（走 CLI 入口）:
1. client_op(uploadAudio)  → 上传音色 wav 到 /voice/uploadAudio
2. world_op(get)            → 获取世界数据
3. 修改角色的 voice 字段（voiceReferenceAudioPath / voiceReferenceAudioName / voice / voiceMode）
4. world_op(save_update)    → 保存世界更新

角色字段对照（参考 voice_file_upload.md 实测）:
- voiceMode                    → "clone"（音色克隆模式）
- voice                        → "克隆：{fileName}"
- voiceReferenceAudioPath      → 服务器返回的 /1/voice/{uuid}.wav
- voiceReferenceAudioName      → 原文件名
- voiceReferenceText           → （可选）参考文本

用法:
    from src.toonflow.workflow.workflow_voice_file_up_save import (
        upload_role_voice_and_save,
    )

    upload_role_voice_and_save(
        story_name="谁让这个山大王修仙的",
        role_name="陆川",
        audio_path=Path("audio/陆川_voice.wav"),
        voice_mode="clone",
        reference_text="",
        project_id=1,
    )

命令行:
    python -m src.cli workflow voice-file-up-save \\
        --story 谁让这个山大王修仙的 \\
        --role-name 陆川 \\
        --audio audio/陆川_voice.wav \\
        --voice-mode clone
"""
import json
from pathlib import Path

from src.toonflow.client import client_op, world_op


def upload_role_voice_and_save(
    story_name: str,
    role_name: str,
    audio_path: Path,
    voice_mode: str = "clone",
    reference_text: str = "",
    project_id: int = 1,
    save: bool = True,
    is_player: bool = False,
) -> dict:
    """
    上传角色音色文件并保存到故事（走 world_op / client_op 入口）

    Args:
        story_name: 故事名称
        role_name: 角色名（按 name 字段匹配；玩家角色对应 world.playerRole）
        audio_path: 音频文件路径（wav/mp3 等）
        voice_mode: 音色模式（默认 "clone"，按 voice_file_upload.md 实测）
        reference_text: 参考文本（可选，存到 voiceReferenceText 字段）
        project_id: 项目 ID
        save: 是否保存到服务器（默认 True）
        is_player: 是否为玩家角色（走 world.playerRole 路径）

    Returns:
        包含上传结果的字典 {role_name, audio_path, voice_reference_path, role, world}
    """
    if not audio_path or not audio_path.exists():
        raise FileNotFoundError(f"音色文件不存在: {audio_path}")

    target_label = "玩家角色" if is_player else "角色"
    print("=" * 60)
    print(f"{target_label}音色文件上传与绑定")
    print(f"故事: {story_name}")
    print(f"{target_label}: {role_name}")
    print(f"音色文件: {audio_path.name}")
    print("=" * 60)

    result = {
        "role_name": role_name,
        "is_player": is_player,
        "audio_path": str(audio_path),
        "voice_reference_path": None,
        "voice_reference_name": audio_path.name,
        "voice_mode": voice_mode,
        "reference_text": reference_text,
        "role": None,
        "world": None,
    }

    # 1. client_op(uploadAudio) - 上传音色
    print("\n[1/4] 上传音色文件...")
    voice_path = client_op(
        op="uploadAudio",
        entry_json=str(audio_path),
        project_id=project_id,
    )
    if not voice_path:
        raise Exception("音色上传失败")
    result["voice_reference_path"] = voice_path
    print(f"  ✓ 服务器路径: {voice_path}")

    # 2. world_op(get) - 获取世界数据
    print("\n[2/4] 获取世界数据...")
    world = world_op(story_name=story_name, op="get")
    if not world:
        raise Exception("无法获取世界数据")
    result["world"] = world
    print(f"  ✓ 世界: {world.get('name')} (id={world.get('id')})")

    # 找到目标对象
    if is_player:
        target = world.get("playerRole")
        if isinstance(target, str):
            target = json.loads(target)
        if not target or target.get("name") != role_name:
            raise ValueError(
                f"未找到玩家角色: {role_name}"
                f"（playerRole.name={target.get('name') if target else None}）"
            )
        result["role"] = target
        print(f"  ✓ 找到玩家角色: {role_name} (id={target.get('id')})")
    else:
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
            raise ValueError(
                f"未找到角色: {role_name}（world 中现有角色: {[r.get('name') for r in roles]}）"
            )
        result["role"] = target
        print(f"  ✓ 找到角色: {role_name} (id={target.get('id')})")

    # 3. 修改角色 voice 字段（参考 voice_file_upload.md 实测）
    print("\n[3/4] 写入 voice 字段...")
    target["voiceMode"] = voice_mode
    target["voice"] = f"克隆：{audio_path.name}"
    target["voiceReferenceAudioPath"] = voice_path
    target["voiceReferenceAudioName"] = audio_path.name
    if reference_text:
        target["voiceReferenceText"] = reference_text
    # 旧值清掉（防服务器残留影响）
    target["voicePresetId"] = ""
    target["voicePromptText"] = ""
    print(f"  ✓ voiceMode={voice_mode}")
    print(f"  ✓ voiceReferenceAudioPath={voice_path}")

    # 4. world_op(save_update) - 保存世界
    if save:
        print(f"\n[4/4] 保存世界: {role_name} 音色已绑定")

        if is_player:
            world["playerRole"] = json.dumps(target, ensure_ascii=False)
        else:
            world["settings"] = json.dumps(settings, ensure_ascii=False)

        saved = world_op(
            story_name=story_name,
            op="save_update",
            entry_json=json.dumps(world, ensure_ascii=False),
        )
        result["world"] = saved
        print(f"  ✓ {target_label} {role_name} 音色已绑定到世界")
    else:
        print(f"\n[4/4] 跳过保存（save=False）")

    print("\n" + "=" * 60)
    print("完成!")
    print(f"  音色文件: {audio_path.name}")
    print(f"  服务器路径: {voice_path}")
    print(f"  模式: {voice_mode}")
    print("=" * 60)

    return result


def workflow_voice_file_up_save(
    story_name: str = None,
    role_name: str = None,
    audio: str = None,
    voice_mode: str = "clone",
    reference_text: str = "",
    project_id: int = 1,
    is_player: bool = False,
):
    """
    CLI 入口：角色音色文件上传与绑定工作流

    Args:
        story_name: 故事名称
        role_name: 角色名
        audio: 音色文件路径
        voice_mode: 音色模式（默认 clone）
        reference_text: 参考文本
        project_id: 项目 ID
        is_player: 是否为玩家角色
    """
    if not role_name:
        raise ValueError("需要 --role-name 参数")
    if not audio:
        raise ValueError("需要 --audio 参数")

    return upload_role_voice_and_save(
        story_name=story_name,
        role_name=role_name,
        audio_path=Path(audio),
        voice_mode=voice_mode,
        reference_text=reference_text,
        project_id=project_id,
        save=True,
        is_player=is_player,
    )