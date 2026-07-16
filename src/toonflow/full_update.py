"""
一键完整更新：世界 + 玩家角色 + NPC角色 + 章节 + 封面

用法:
    from src.toonflow.full_update import full_update
    full_update("破局-从冷落走到瞩目")

    或命令行:
    python -m src.cli toonflow update --story 破局-从冷落走到瞩目
"""
import json
from pathlib import Path

from src.config import load_config
from src.toonflow.client import ToonflowClient
from src.toonflow.roles import update_player_role, update_npc_roles
from src.toonflow.chapters import update_chapters
from src.toonflow.covers import upload_world_covers


def full_update(story_name: str = None):
    """
    完整更新流程:
    1. 创建/更新世界
    2. 玩家角色
    3. NPC角色 + 头像分离
    4. 章节
    5. 封面/背景图
    6. 保存最终配置
    """
    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError(f"未指定故事名，且 .env 中无 CURRENT_STORY")

    print("=" * 60)
    print(f"发布故事: {story.story_name}")
    print(f"环境: {global_cfg.base_url}")
    print(f"World ID: {story.world_id}")
    print("=" * 60)

    client = ToonflowClient(global_cfg)

    # 1. 创建或更新世界
    print("\n[1/5] 创建/更新世界...")
    world_data = None
    if story.world_id:
        try:
            world_data = client.get_world(story.world_id)
        except Exception:
            pass

    if world_data:
        settings = world_data.get("settings", {})
        if isinstance(settings, str):
            settings = json.loads(settings)
        settings["globalBackground"] = story.global_bg
        world_data["settings"] = settings
        world_data["name"] = story.story_name
        world_data["intro"] = story.intro
        world_id = world_data.get("id", story.world_id)
        print(f"  -> 更新现有世界 (ID={world_id})")
    else:
        # 创建新世界
        world_data = client.create_world(
            story.project_id, story.story_name, story.intro, story.global_bg
        )
        world_id = world_data.get("id")
        print(f"  ✓ 世界创建成功 (ID={world_id})")
        # 更新 story.world_id
        story.world_id = world_id
        # 保存 WORLD_ID 到故事 .env
        _save_world_id(story)

    world_data["id"] = world_id
    world_data["worldId"] = world_id

    # 2. 玩家角色
    print("\n[2/5] 处理玩家角色...")
    world_data = update_player_role(client, story, world_data)

    # 3. NPC角色
    print("\n[3/5] 处理NPC角色...")
    world_data = update_npc_roles(client, story, world_data)

    # 保存世界（角色数据）
    print("\n  保存角色数据...")
    client.save_world(world_data)

    # 4. 章节
    print("\n[4/5] 处理章节...")
    update_chapters(client, story, world_data)

    # 5. 封面/背景图
    print("\n[5/5] 上传封面和背景图...")
    world_data = upload_world_covers(client, story, world_data)

    # 最终保存
    print("\n  保存最终配置...")
    client.save_world(world_data)

    print(f"\n{'='*60}")
    print("发布完成!")
    print(f"世界ID: {world_id}")
    print(f"故事名: {story.story_name}")
    print(f"{'='*60}")

    return world_id


def _save_world_id(story):
    """保存 WORLD_ID 到故事 .env"""
    from src.config import _parse_env_file
    env_path = story.story_dir / ".env"
    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith("WORLD_ID="):
            new_lines.append(f"WORLD_ID={story.world_id}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"WORLD_ID={story.world_id}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)