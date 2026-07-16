"""
角色卡构建器：Toonflow MD -> SillyTavern V2 JSON + PNG

功能:
1. 读取 Toonflow 角色 MD 文件
2. 解析参数卡 JSON + 文本设定
3. 转换为 SillyTavern V2 角色卡格式 (chara_card_v2)
4. 将 JSON 以 base64 嵌入头像 PNG 的 tEXt chunk (keyword=chara)
5. 同时输出独立 JSON 版本
"""
import json
import re
from pathlib import Path

from src.config import load_config, StoryConfig
from src.md_parser import parse_role_md
from src.png_utils import embed_card_to_png, verify_chara_chunk


def build_v2_card(role_name: str, parsed, story: StoryConfig, is_player: bool = False) -> dict:
    """
    将解析的角色数据转换为 SillyTavern V2 角色卡格式

    Args:
        role_name: 角色名
        parsed: ParsedRole 对象
        story: 故事配置
        is_player: 是否是玩家角色
    """
    card = parsed.parameter_card or {}

    # 构建 description
    desc_parts = []
    if card.get("raw_setting"):
        desc_parts.append(card["raw_setting"])

    # 把参数卡字段拼成完整描述
    lines = []
    if card.get("personality"):
        lines.append(f"性格: {card['personality']}")
    if card.get("appearance"):
        lines.append(f"外貌: {card['appearance']}")
    if card.get("voice"):
        lines.append(f"音色特点: {card['voice']}")
    if card.get("skills"):
        skills = card["skills"]
        if isinstance(skills, list):
            lines.append(f"技能: {', '.join(skills)}")
        else:
            lines.append(f"技能: {skills}")
    if card.get("items"):
        items = card["items"]
        if isinstance(items, list):
            lines.append(f"物品: {', '.join(items)}")
        else:
            lines.append(f"物品: {items}")
    if card.get("equipment"):
        equip = card["equipment"]
        if isinstance(equip, list):
            lines.append(f"装备: {', '.join(equip)}")
        else:
            lines.append(f"装备: {equip}")
    if card.get("level"):
        level_desc = card.get("level_desc", "")
        lines.append(f"等级: {card['level']}" + (f" ({level_desc})" if level_desc else ""))
    if card.get("hp"):
        lines.append(f"血量: {card['hp']}")
    if card.get("mp"):
        lines.append(f"蓝量: {card['mp']}")
    if card.get("money"):
        lines.append(f"金钱: {card['money']}")
    if card.get("other"):
        other = card["other"]
        if isinstance(other, list):
            lines.append(f"其他: {', '.join(other)}")
        else:
            lines.append(f"其他: {other}")

    if lines:
        desc_parts.append("\n".join(lines))

    description = "\n\n".join(desc_parts) if desc_parts else card.get("raw_setting", "")

    # 构建 tags
    tags = list(story.card_tags) if story.card_tags else ["Roleplay"]
    if is_player:
        if "玩家角色" not in tags:
            tags.append("玩家角色")
    else:
        if "NPC" not in tags:
            tags.append("NPC")

    # 构建 V2 卡片
    v2_card = {
        "spec": "chara_card_v2",
        "spec_version": "2.0",
        "data": {
            "name": role_name,
            "description": description,
            "personality": card.get("personality", ""),
            "scenario": story.card_scenario or story.global_bg,
            "first_mes": _build_first_mes(role_name, card, is_player, story),
            "mes_example": "",
            "alternate_greetings": [],
            "character_book": None,
            "tags": tags,
            "creator": "Toonflow",
            "character_version": "1.0",
            "extensions": {
                "toonflow": {
                    "raw_setting": card.get("raw_setting", ""),
                    "gender": card.get("gender", ""),
                    "age": card.get("age", 0),
                    "level": card.get("level", 1),
                    "level_desc": card.get("level_desc", ""),
                    "appearance": card.get("appearance", ""),
                    "voice_prompt": parsed.voice_prompt_text,
                    "avatar_prompt": parsed.avatar_image_prompt,
                    "skills": card.get("skills", []),
                    "items": card.get("items", []),
                    "equipment": card.get("equipment", []),
                    "hp": card.get("hp", 100),
                    "mp": card.get("mp", 50),
                    "money": card.get("money", 0),
                    "other": card.get("other", []),
                    "exp": card.get("exp", 0),
                    "next_level_exp": card.get("next_level_exp", 100),
                    "is_player": is_player,
                }
            },
        },
    }

    return v2_card


def _build_first_mes(role_name: str, card: dict, is_player: bool, story: StoryConfig) -> str:
    """生成角色开场白"""
    raw_setting = card.get("raw_setting", "")

    # 玩家角色开场白
    if is_player:
        return (
            f"*你进入了「{story.story_name}」的世界。*\n\n"
            f"*{raw_setting[:100]}...*\n\n"
            f"故事即将开始..."
        )

    # NPC 通用开场白
    return (
        f"*{role_name}出现在你的面前。*\n\n"
        f"\"{raw_setting[:80]}...\""
    )


def build_all_cards(story_name: str = None, output_subdir: str = None) -> list:
    """
    为故事的所有角色生成角色卡

    Args:
        story_name: 故事名（不指定则从 .env CURRENT_STORY 读取）
        output_subdir: 输出子目录名（如 "chub_ai"），默认为故事名目录

    Returns:
        成功生成的角色卡列表 [{name, json_path, png_path}]
    """
    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError("未指定故事名")

    output_dir = story.cards_output_dir
    if output_subdir:
        output_dir = output_dir / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Toonflow -> SillyTavern V2 角色卡转换器")
    print(f"故事: {story.story_name}")
    print(f"输出: {output_dir}")
    print("=" * 60)

    results = []
    all_roles = []

    # 玩家角色
    if story.player_role:
        all_roles.append((story.player_role, True))

    # NPC 角色
    for r in story.npc_roles:
        all_roles.append((r, False))

    for i, (role_mapping, is_player) in enumerate(all_roles, 1):
        name = role_mapping.name
        md_path = story.roles_dir / role_mapping.md_file
        avatar_path = story.avatars_dir / role_mapping.avatar_file if role_mapping.avatar_file else None

        print(f"\n[{i}/{len(all_roles)}] {name}")

        if not md_path.exists():
            print(f"  ✗ MD 不存在: {md_path}")
            continue

        # 解析
        parsed = parse_role_md(md_path, forced_name=name)

        # 构建 V2 卡片
        v2_card = build_v2_card(name, parsed, story, is_player)

        # 输出 JSON
        json_path = output_dir / f"{name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(v2_card, f, ensure_ascii=False, indent=2)
        print(f"  ✓ JSON: {json_path.name}")

        # 嵌入 PNG
        png_path = output_dir / f"{name}.png"
        if avatar_path and avatar_path.exists():
            try:
                embed_card_to_png(v2_card, str(avatar_path), str(png_path))
                # 验证
                valid, spec = verify_chara_chunk(str(png_path))
                if valid:
                    print(f"  ✓ PNG: {png_path.name} (spec: {spec})")
                else:
                    print(f"  ⚠ PNG tEXt 验证失败")
            except Exception as e:
                print(f"  ✗ PNG 嵌入失败: {e}")
        else:
            print(f"  ⚠ 无头像，跳过 PNG")

        results.append({"name": name, "json_path": json_path, "png_path": png_path})

    # 生成索引
    _generate_index(output_dir, all_roles, story.story_name)

    print(f"\n{'='*60}")
    print(f"完成！成功 {len(results)} 个角色卡")
    print(f"输出目录: {output_dir}")
    print(f"{'='*60}")

    return results


def _generate_index(output_dir: Path, all_roles, story_name: str):
    """生成 INDEX.md 索引文件"""
    index_path = output_dir / "INDEX.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(f"# {story_name} - 角色卡仓库\n\n")
        f.write(f"共 {len(all_roles)} 个角色卡（SillyTavern V2 格式）\n\n")
        f.write("| 角色名 | 类型 | PNG | JSON |\n")
        f.write("|--------|------|-----|------|\n")
        for role, is_player in all_roles:
            name = role.name
            rtype = "玩家" if is_player else "NPC"
            png_ok = (output_dir / f"{name}.png").exists()
            json_ok = (output_dir / f"{name}.json").exists()
            f.write(f"| {name} | {rtype} | {'✅' if png_ok else '❌'} | {'✅' if json_ok else '❌'} |\n")