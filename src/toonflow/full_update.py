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
        except Exception as e:
            # 服务器对"不存在"和"无权限"统一返回 403，
            # 无法区分——安全策略：视为不存在，直接重建
            print(f"  ⚠ 世界 {story.world_id} 不可访问 ({str(e)[:80]})，将重建")
            story.world_id = 0

    if world_data:
        # --- 更新路径 ---
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
        # --- 创建路径 ---
        # 注意：即使 story.world_id=0 也走这里，让 saveWorld(worldId=0) 去决定是创建还是更新
        world_data = {
            "projectId": story.project_id,
            "name": story.story_name,
            "intro": story.intro,
            "worldId": story.world_id or 0,   # 0=创建，非0=带ID创建（服务端视具体实现）
            "settings": json.dumps({
                "roles": [],
                "globalBackground": story.global_bg
            })
        }
        result = client.api_call("/game/saveWorld", world_data)
        if result.get("code") == 200:
            world_data = result.get("data", {})
            world_id = world_data.get("id")
            print(f"  ✓ 世界创建成功 (ID={world_id})")
            story.world_id = world_id
            _save_world_id(story)
        else:
            raise RuntimeError(f"创建世界失败: {result}")

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
    """保存 WORLD_ID 到 story.json"""
    story_json_path = story.story_dir / "story.json"
    if not story_json_path.exists():
        return

    with open(story_json_path, "r", encoding="utf-8") as f:
        story_json = json.load(f)

    story_json["world_id"] = story.world_id

    with open(story_json_path, "w", encoding="utf-8") as f:
        json.dump(story_json, f, ensure_ascii=False, indent=2)