"""
角色更新：玩家角色 + NPC 角色（头像分离、音色提示词）

流程:
1. 解析 MD 文件
2. 上传头像 + 人体分离
3. 构建 role 对象
4. 更新到世界 settings.roles / playerRole
"""
import json
from pathlib import Path

from src.config import StoryConfig
from src.md_parser import parse_role_md
from src.toonflow.client import ToonflowClient


def build_role_object(parsed, role_name: str, avatar_result: dict = None, is_player: bool = False) -> dict:
    """构建 Toonflow 角色对象"""
    role_obj = {
        "roleType": "player" if is_player else "npc",
        "name": parsed.name or role_name,
        "description": parsed.description,
        "avatarImagePrompt": parsed.avatar_image_prompt,
        "voiceMode": parsed.voice_mode,
        "voicePromptText": parsed.voice_prompt_text,
        "parameterCardJson": parsed.parameter_card,
    }
    if avatar_result:
        role_obj.update(avatar_result)
    if is_player:
        role_obj["id"] = "player"
    return role_obj


def update_player_role(client: ToonflowClient, story: StoryConfig, world_data: dict) -> dict:
    """处理玩家角色"""
    if not story.player_role:
        print("  ⚠ 无玩家角色配置，跳过")
        return world_data

    md_path = story.roles_dir / story.player_role.md_file
    if not md_path.exists():
        print(f"  ⚠ 玩家角色文件不存在: {md_path}")
        return world_data

    print(f"  处理玩家角色: {story.player_role.name}")
    parsed = parse_role_md(md_path, role_type="player", forced_name=story.player_role.name)

    # 头像分离
    avatar_result = {}
    avatar_path = story.avatars_dir / story.player_role.avatar_file
    if avatar_path.exists():
        avatar_result = client.separate_avatar(avatar_path, story.player_role.name, story.world_id)

    player_data = build_role_object(parsed, story.player_role.name, avatar_result, is_player=True)
    # 玩家角色保留 avatarPath（头像），但不需要分离的背景图路径
    player_data.pop("avatarSourcePath", None)
    player_data.pop("avatarBgPath", None)

    world_data["playerRole"] = player_data
    print(f"  ✓ 玩家角色: {player_data.get('name')}")
    return world_data


def update_npc_roles(client: ToonflowClient, story: StoryConfig, world_data: dict) -> dict:
    """处理 NPC 角色"""
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)

    roles = settings.get("roles", [])
    existing_map = {r.get("name"): r for r in roles}

    for role_mapping in story.npc_roles:
        md_path = story.roles_dir / role_mapping.md_file
        if not md_path.exists():
            print(f"  ⚠ 跳过(文件不存在): {md_path}")
            continue

        print(f"\n  处理: {role_mapping.name}")
        parsed = parse_role_md(md_path, forced_name=role_mapping.name)

        # 头像分离
        avatar_result = {}
        if role_mapping.avatar_file:
            avatar_path = story.avatars_dir / role_mapping.avatar_file
            if avatar_path.exists():
                avatar_result = client.separate_avatar(avatar_path, role_mapping.name, story.world_id)
            else:
                print(f"    ⚠ 头像不存在: {avatar_path}")

        role_obj = build_role_object(parsed, role_mapping.name, avatar_result, is_player=False)

        # 检查是否已存在
        if role_mapping.name in existing_map:
            existing = existing_map[role_mapping.name]
            for k, v in role_obj.items():
                if v and k != "id":
                    existing[k] = v
            print(f"    ✓ 更新现有角色")
        else:
            roles.append(role_obj)
            print(f"    ✓ 添加新角色")

    settings["roles"] = roles
    world_data["settings"] = settings
    return world_data