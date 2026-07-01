#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
《破局-从冷落走到瞩目》故事发布脚本
路径：ai_story/171/破局-从冷落走到瞩目
环境：生产环境 (122.51.232.171:60002)

功能：
1. 创建新世界
2. 玩家角色(playerRole)
3. NPC角色 + 头像分离
4. 章节内容
5. 封面和背景图
"""

import requests
import json
import base64
import os
import re
from pathlib import Path

# ============ 配置（从 .env 读取）============
BASE_URL = "http://122.51.232.171:60002"
TOKEN = "xxx"
PROJECT_ID = 1
WORLD_ID = 36  # 已创建的世界36

BASE_DIR = Path("D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/171/破局-从冷落走到瞩目")
ROLES_DIR = BASE_DIR / "roles"
AVATARS_DIR = BASE_DIR / "avatars"
CHAPTERS_DIR = BASE_DIR / "chapters"
IMAGE_DIR = BASE_DIR / "image"

# 故事名称
STORY_NAME = "破局-从冷落走到瞩目"

# 故事简介
STORY_INTRO = """顾泽是顾家亲生儿子，出生时被护士狸猫换太子与顾子航身份互换。十八年后真相大白，顾家却选择继续留养养子顾子航，将亲生儿子顾泽视为弃子。绝望后的顾泽彻底清醒，不再奢求顾家的认可，凭实力在锐星贵族学校逆袭，用成绩和实力打脸顾家，最终成为商业帝国的新贵。"""

# 全局背景（AI 运行时参考的重要信息）
STORY_GLOBAL_BG = """【故事背景】
顾泽是顾家亲生儿子，出生时被护士狸猫换太子与顾子航身份互换。十八年后真相大白，顾家却选择继续留养养子顾子航，将亲生儿子顾泽视为弃子。
绝望后的顾泽彻底清醒，不再奢求顾家的认可，凭实力在锐星贵族学校逆袭，用成绩和实力打脸顾家，最终成为商业帝国的新贵。

【重要人物关系】
• 顾父：顾家老爷，城府极深，偏向养子顾子航
• 顾母：顾家太太，表面温和，内心同样偏向顾子航
• 顾子航：假少爷，心机深沉，处处针对顾泽
• 顾家大姐/二姐：对顾泽冷淡，视为外人
• 温知予：温父之女，锐星学校学生，聪慧冷静，是顾泽的重要伙伴
• 温父：锐星学校校长，学者气质，与顾家有旧交
• 顾泽小弟：顾泽暗中培养的心腹，38岁，负责情报工作

【世界观设定】
• 顾家：海城顶级豪门，涉及政商两界
• 锐星贵族学校：海城最顶尖的贵族学校，学生非富即贵
• 白家：与顾家相当的豪门世家
• 顾泽流落在外时被海外势力培养，具备超常的商业和战斗能力"""

# NPC角色映射（角色名 -> MD文件名）
ROLE_NAME_TO_FILE = {
    "顾子航": "顾子航.md",
    "顾父": "顾铭远(顾父).md",
    "顾母": "林雅芝(顾母).md",
    "顾家大姐": "顾念瑶(大姐).md",
    "顾家二姐": "顾念卿(二姐).md",
    "顾家下人": "顾家下人.md",
    "温知予": "温知予.md",
    "温父": "温父.md",
    "顾泽小弟": "陈浩(顾泽手下).md",
    "白家千金": "白家千金.md",
    "路人甲": "路人甲.md",
}

# 角色名 -> 头像文件
ROLE_NAME_TO_AVATAR = {
    "顾子航": "顾子航.png",
    "顾父": "顾父.png",
    "顾母": "顾母.png",
    "顾家大姐": "顾家大姐.png",
    "顾家二姐": "顾家二姐.png",
    "顾家下人": "顾家下人.png",
    "温知予": "温知予.png",
    "温父": "温父.png",
    "顾泽小弟": "顾泽小弟.png",
    "白家千金": "白家千金.png",
    "路人甲": "路人甲.png",
}

# ============ 工具函数 ==================

def api_call(path, data):
    """调用 API"""
    url = f"{BASE_URL}{path}"
    resp = requests.post(url, json=data, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=60)
    return resp.json()


def parse_md_role(file_path, role_type="npc"):
    """解析 MD 文件，提取角色设定"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    role_data = {
        "roleType": role_type,
        "description": "",
        "avatarImagePrompt": "",
        "avatarBgPrompt": "",
        "voiceMode": "prompt_voice",
        "voicePromptText": "",
        "parameterCardJson": None,
    }

    # 提取名称
    name_match = re.search(r"^#\s*(.+)", content, re.MULTILINE)
    if name_match:
        role_data["name"] = name_match.group(1).strip()

    # 提取角色设定
    setting_match = re.search(r"## 角色设定.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not setting_match:
        setting_match = re.search(r"角色设定.*?：(.*?)(?=\n##|\n```|\Z)", content, re.DOTALL)
    if setting_match:
        role_data["description"] = setting_match.group(1).strip()

    # 提取头像描述
    avatar_match = re.search(r"## 头像.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if avatar_match:
        avatar_section = avatar_match.group(1)
        fg_match = re.search(r"\*\*前景\*\*[：:]\s*(.+?)(?=\n\s*[-*]|\n##|\Z)", avatar_section, re.DOTALL)
        if fg_match:
            role_data["avatarImagePrompt"] = fg_match.group(1).strip()
        bg_match = re.search(r"\*\*背景\*\*[：:]\s*(.+)", avatar_section, re.DOTALL)
        if bg_match:
            role_data["avatarBgPrompt"] = bg_match.group(1).strip()

    # 提取语音提示词
    voice_match = re.search(r"## 语音.*?\n.*?\*\*提示词\*\*[：:]\s*(.+?)(?=\n\s*[-*]|\n##|\Z)", content, re.DOTALL)
    if voice_match:
        role_data["voicePromptText"] = voice_match.group(1).strip()

    # 提取参数卡 JSON
    json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if json_match:
        try:
            role_data["parameterCardJson"] = json.loads(json_match.group(1))
        except:
            pass

    return role_data


def separate_avatar(avatar_path, role_name, world_id):
    """上传头像并进行人体分离"""
    print(f"    → 分离头像: {avatar_path.name}")

    with open(avatar_path, "rb") as f:
        img_data = f.read()
    base64_data = base64.b64encode(img_data).decode("utf-8")

    result = api_call("/game/separateRoleAvatar", {
        "worldId": world_id,
        "base64Data": base64_data,
        "roleName": role_name
    })

    if result.get("code") == 200:
        data = result.get("data", {})
        return {
            "avatarSourcePath": data.get("sourceFilePath", ""),
            "avatarPath": data.get("foregroundFilePath", ""),
            "avatarBgPath": data.get("backgroundFilePath", ""),
        }
    else:
        print(f"    ✗ 分离失败: {result.get('message', str(result))}")
        return {}


def save_chapter(chapter_data, world_id, existing_chapter_id=None):
    """保存章节（存在则更新，否则创建）"""
    chapter_data["worldId"] = world_id
    chapter_data["status"] = "draft"
    if existing_chapter_id:
        chapter_data["chapterId"] = existing_chapter_id
        chapter_data["id"] = existing_chapter_id
        result = api_call("/game/saveChapter", chapter_data)
        if result.get("code") == 200:
            print(f"    ✓ 章节更新: {chapter_data.get('title', '')} (ID={existing_chapter_id})")
            return result.get("data", {})
        else:
            print(f"    ✗ 章节更新失败: {result}")
            return None
    else:
        result = api_call("/game/saveChapter", chapter_data)
        if result.get("code") == 200:
            print(f"    ✓ 章节创建: {chapter_data.get('title', '')} (ID={result['data'].get('id')})")
            return result.get("data", {})
        else:
            print(f"    ✗ 章节创建失败: {result}")
            return None


def upload_image(file_path, image_type="scene"):
    """上传图片"""
    if not os.path.exists(file_path):
        print(f"    ✗ 文件不存在: {file_path}")
        return None

    with open(file_path, "rb") as f:
        image_data = f.read()

    ext = Path(file_path).suffix.lower().strip(".")
    if ext == "jpeg":
        ext = "jpg"

    mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    base64_data = f"data:{mime_type};base64,{base64.b64encode(image_data).decode('utf-8')}"

    print(f"    上传: {file_path.name}")
    result = api_call("/game/uploadImage", {
        "projectId": PROJECT_ID,
        "type": "scene",
        "fileName": f"{image_type}_{Path(file_path).stem}.{ext}",
        "base64Data": base64_data
    })

    if result.get("code") == 200:
        path = result.get("data", {}).get("filePath")
        print(f"    ✓ 上传成功: {path}")
        return path
    else:
        print(f"    ✗ 上传失败: {result.get('message')}")
        return None


def parse_chapter_md(file_path):
    """解析章节MD文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chapter_data = {
        "title": "",
        "content": "",
        "backgroundPrompt": "",
        "openingRole": "旁白",
        "openingText": "",
    }

    # 提取标题
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if title_match:
        chapter_data["title"] = title_match.group(1).strip()

    # 提取开场白
    narrator_match = re.search(r"@旁白[：:]\s*(.+?)(?=\n@|\n##|\Z)", content, re.DOTALL)
    if narrator_match:
        chapter_data["openingText"] = narrator_match.group(1).strip()[:200]

    # 提取正文内容（去掉非事件部分）
    # 移除 ## 非事件 开头的所有内容
    content_only = re.sub(r"## 非事件.*", "", content, flags=re.DOTALL)
    # 清理 markdown 格式，保留台词
    lines = content_only.split("\n")
    clean_lines = []
    for line in lines:
        line = line.strip()
        # 跳过章节标题、阶段标题、注释
        if line.startswith("#") or line.startswith(">") or line.startswith("```"):
            continue
        # 跳过空行
        if not line:
            continue
        clean_lines.append(line)

    chapter_data["content"] = "\n".join(clean_lines)

    return chapter_data


# ============ 主流程 ==================

def main():
    print("=" * 60)
    print(f"发布故事: {STORY_NAME}")
    print("=" * 60)

    # 1. 创建或更新世界
    print("\n[1/6] 创建/更新世界...")
    
    # 先尝试获取现有世界
    existing_world_id = None
    resp = api_call("/game/getWorld", {"worldId": WORLD_ID}) if WORLD_ID else None
    if resp and resp.get("code") == 200 and resp.get("data"):
        existing_world_id = resp["data"].get("id")
    
    if existing_world_id:
        # 更新现有世界
        resp = api_call("/game/getWorld", {"worldId": existing_world_id})
        world_data = resp.get("data", {})
        # 解析 settings（可能是 JSON 字符串）
        settings = world_data.get("settings", {})
        if isinstance(settings, str):
            settings = json.loads(settings)
        settings["globalBackground"] = STORY_GLOBAL_BG
        world_data["settings"] = json.dumps(settings)
        world_data["name"] = STORY_NAME
        world_data["intro"] = STORY_INTRO
        world_id = existing_world_id
        print(f"  → 更新现有世界 (ID={world_id})")
    else:
        # 创建新世界
        world_data = {
            "projectId": PROJECT_ID,
            "name": STORY_NAME,
            "intro": STORY_INTRO,
            "worldId": 0,
            "settings": json.dumps({
                "roles": [],
                "globalBackground": STORY_GLOBAL_BG
            })
        }
        result = api_call("/game/saveWorld", world_data)
        if result.get("code") == 200:
            saved_world = result.get("data", {})
            world_id = saved_world.get("id")
            print(f"  ✓ 世界创建成功 (ID={world_id})")
        else:
            print(f"  ✗ 世界创建失败: {result}")
            return
    
    world_data["id"] = world_id
    world_data["worldId"] = world_id

    # 2. 处理玩家角色
    print("\n[2/6] 处理玩家角色...")
    player_md = ROLES_DIR / "顾泽.md"
    if player_md.exists():
        player_data = parse_md_role(player_md, "player")
        player_data["id"] = "player"
        player_data.pop("avatarSourcePath", None)
        player_data.pop("avatarPath", None)
        player_data.pop("avatarBgPath", None)

        # 头像分离
        avatar_path = AVATARS_DIR / "顾泽.png"
        if avatar_path.exists():
            avatar_result = separate_avatar(avatar_path, "顾泽", world_id)
            player_data.update(avatar_result)

        # 保存玩家角色
        world_data["playerRole"] = player_data
        print(f"  ✓ 玩家角色: {player_data.get('name', '顾泽')}")
    else:
        print(f"  ✗ 玩家角色文件不存在")

    # 3. 处理NPC角色
    print("\n[3/6] 处理NPC角色...")
    roles = []

    for role_name, md_file in ROLE_NAME_TO_FILE.items():
        md_path = ROLES_DIR / md_file
        if not md_path.exists():
            print(f"    ⚠ 跳过: {md_path}")
            continue

        print(f"\n  处理: {role_name}")
        role_data = parse_md_role(md_path)

        # 头像分离
        avatar_file = ROLE_NAME_TO_AVATAR.get(role_name)
        avatar_path = AVATARS_DIR / avatar_file if avatar_file else None
        avatar_result = {}

        if avatar_path and avatar_path.exists():
            avatar_result = separate_avatar(avatar_path, role_name, world_id)

        # 构建角色对象
        role_obj = {
            "roleType": "npc",
            "name": role_data.get("name", role_name),
            "description": role_data.get("description", ""),
            "avatarImagePrompt": role_data.get("avatarImagePrompt", ""),
            "voiceMode": "prompt_voice",
            "voicePromptText": role_data.get("voicePromptText", ""),
            "parameterCardJson": role_data.get("parameterCardJson"),
        }
        role_obj.update(avatar_result)
        roles.append(role_obj)
        print(f"    ✓ 添加角色")

    # 保存角色（更新到现有世界）
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    settings["roles"] = roles
    world_data["settings"] = json.dumps(settings)
    world_data["worldId"] = world_id
    result = api_call("/game/saveWorld", world_data)
    if result.get("code") == 200:
        print(f"\n  ✓ 角色保存成功 ({len(roles)}个NPC)")
    else:
        print(f"  ✗ 角色保存失败: {result}")

    # 4. 处理章节（含背景图）
    print("\n[4/6] 处理章节...")
    chapter_ids = []

    # 先通过 getWorld 获取 chapterCount，然后遍历找到现有章节
    resp = api_call("/game/getWorld", {"worldId": world_id, "projectId": PROJECT_ID})
    chapter_count = 0
    existing_chapters_by_title = {}
    if resp.get("code") == 200:
        chapter_count = resp.get("data", {}).get("chapterCount", 0)
        print(f"  现有章节数(总): {chapter_count}")
        # 尝试获取章节列表（有些版本 chapters 在 data 里）
        data = resp.get("data", {})
        chapters_list = data.get("chapters", [])
        if chapters_list:
            existing_chapters_by_title = {ch.get("title", ""): ch for ch in chapters_list}
            print(f"  从 getWorld 获取到 {len(existing_chapters_by_title)} 个章节")
        else:
            # 按 ID 遍历查找属于 world_id 的章节（扩大范围）
            for cid in range(1, 200):
                ch_resp = api_call("/game/getChapter", {"chapterId": cid, "worldId": world_id})
                if ch_resp.get("code") == 200 and ch_resp.get("data"):
                    ch = ch_resp["data"]
                    if ch.get("worldId") == world_id:
                        existing_chapters_by_title[ch.get("title", "")] = ch
        print(f"  现有章节: {list(existing_chapters_by_title.keys())}")

    if CHAPTERS_DIR.exists():
        chapter_files = sorted(CHAPTERS_DIR.glob("chapter_*.md"))
        for i, chapter_file in enumerate(chapter_files):
            print(f"\n  章节: {chapter_file.name}")
            chapter_data = parse_chapter_md(chapter_file)
            print(f"    标题: {chapter_data.get('title', '未命名')}")
            print(f"    内容长度: {len(chapter_data.get('content', ''))} 字符")

            # 上传章节封面和背景图
            chapter_num = f"chapter{i+1}"
            covers = list(IMAGE_DIR.glob(f"{chapter_num}_cover__*.jpg"))
            bgs = list(IMAGE_DIR.glob(f"{chapter_num}_bg__*.jpg"))

            if covers:
                path = upload_image(covers[0], f"chapter_{i+1}_cover")
                if path:
                    chapter_data["coverPath"] = path

            if bgs:
                bg_path = upload_image(bgs[0], f"chapter_{i+1}_bg")
                if bg_path:
                    chapter_data["backgroundPath"] = bg_path

            chapter_data["sort"] = i
            # 通过标题匹配现有章节
            existing = existing_chapters_by_title.get(chapter_data.get("title", ""))
            existing_id = existing.get("id") if existing else None
            saved = save_chapter(chapter_data, world_id, existing_id)
            if saved:
                chapter_ids.append(saved.get("id"))

    # 5. 上传世界封面
    print("\n[5/6] 上传世界封面...")
    cover_files = list(IMAGE_DIR.glob("story_cover__*.jpg"))
    if cover_files:
        path = upload_image(cover_files[0], "world_cover")
        if path:
            # 更新 settings 中的 coverPath
            settings = world_data.get("settings", {})
            if isinstance(settings, str):
                settings = json.loads(settings)
            settings["coverPath"] = path
            world_data["settings"] = json.dumps(settings)
            world_data["coverPath"] = path

    # 上传封面背景图（存入 settings.coverBgPath）
    cover_bg_files = list(IMAGE_DIR.glob("story_coverBg__*.jpg"))
    if cover_bg_files:
        bg_path = upload_image(cover_bg_files[0], "world_cover_bg")
        if bg_path:
            settings = world_data.get("settings", {})
            if isinstance(settings, str):
                settings = json.loads(settings)
            settings["coverBgPath"] = bg_path
            world_data["settings"] = json.dumps(settings)
            print(f"    ✓ 封面背景图已设置: {bg_path}")
    else:
        print("    ⚠ 未找到封面背景图 (story_coverBg__*.jpg)")

    # 6. 保存最终配置
    print("\n[6/6] 保存最终配置...")
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    world_data["settings"] = json.dumps(settings)
    world_data["worldId"] = world_id
    result = api_call("/game/saveWorld", world_data)
    if result.get("code") == 200:
        print("  ✓ 最终配置保存成功")
    else:
        print(f"  ✗ 保存失败: {result}")

    print(f"\n{'='*60}")
    print("发布完成!")
    print(f"世界ID: {world_id}")
    print(f"故事名: {STORY_NAME}")
    print(f"NPC角色: {len(roles)}")
    print(f"章节数: {len(chapter_ids)}")


if __name__ == "__main__":
    main()