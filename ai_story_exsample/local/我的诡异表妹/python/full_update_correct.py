#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
角色数据全面更新脚本
路径：ai_story/local/我的诡异表妹
环境：local (localhost:60002)
世界ID：35

功能：
1. 角色设定 - 从 MD 文件读取
2. avatarImagePrompt - 从 MD 文件提取
3. 头像上传和人体分离 - 调用 separateRoleAvatar
4. 音色提示词 - 从 MD 文件提取（不自动生成音色文件）
5. 章节内容 - 从 chapters 读取并保存
"""

import requests
import json
import base64
import os
import re
from pathlib import Path

# 配置
BASE_URL = "http://localhost:60002"
TOKEN = "***REMOVED***"

PROJECT_ID = 1
WORLD_ID = 35

BASE_DIR = Path("/ai_story/local/我的诡异表妹")
ROLES_DIR = BASE_DIR / "roles"
AVATARS_DIR = BASE_DIR / "avatars"
CHAPTERS_DIR = BASE_DIR / "chapters"

# 角色名称到文件的映射（排除 role.list.md, 用户.md）
ROLE_NAME_TO_FILE = {
    "小七": "小七.md",
    "校长": "校长.md",
    "诡异美女老师": "诡异美女老师.md",
    "裂口女": "诡异A（裂口女）.md",
    "无面人": "诡异B（无面人）.md",
    "长发女": "诡异C（长发女）.md",
    "人类学生甲": "人类学生甲.md",
    "人类学生乙": "人类学生乙.md",
    "人类学生丙": "人类学生丙.md",
    "路人甲": "路人甲.md",
}

# 角色名称到头像文件的映射
ROLE_NAME_TO_AVATAR = {
    "小七": "xiaoqi.png",
    "诡异美女老师": "sulaoshi.png",
    "校长": "xiaozhang.png",
    "裂口女": "liekounv.png",
    "无面人": "wumianren.png",
    "长发女": "changfanv.png",
    "人类学生甲": "liming.png",
    "人类学生乙": "wangsiyuan.png",
    "人类学生丙": "zhaoxiaopang.png",
    "路人甲": "lurenjia.png",
}


def api_call(path, data):
    """调用 API"""
    url = f"{BASE_URL}{path}"
    resp = requests.post(url, json=data, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=60)
    return resp.json()


def parse_md_role(file_path):
    """解析 MD 文件，提取角色设定"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    role_data = {
        "roleType": "npc",
        "description": "",
        "avatarImagePrompt": "",
        "avatarBgPrompt": "",
        "voiceMode": "prompt_voice",
        "voicePromptText": "",
        "parameterCardJson": None,
    }

    # 提取名称
    name_match = re.search(r"- \*\*名称\*\*[：:]\s*(.+)", content)
    if name_match:
        role_data["name"] = name_match.group(1).strip()
    
    # 如果没找到，尝试从文件名提取
    if "name" not in role_data:
        name_match = re.search(r"^#\s*(.+)", content, re.MULTILINE)
        if name_match:
            role_data["name"] = name_match.group(1).strip()
    
    # 提取角色设定（从 "## 角色设定" 或 "角色设定(" 到下一个 ## 之前）
    setting_match = re.search(r"## 角色设定.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not setting_match:
        setting_match = re.search(r"角色设定.*?：(.*?)(?=\n##|\n```|\Z)", content, re.DOTALL)
    if setting_match:
        role_data["description"] = setting_match.group(1).strip()

    # 提取头像生图描述
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

    # 提取角色参数卡 JSON
    json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if json_match:
        try:
            role_data["parameterCardJson"] = json.loads(json_match.group(1))
        except:
            pass

    return role_data


def parse_chapter_md(file_path):
    """解析章节 MD 文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    chapter_data = {
        "title": "",
        "content": "",
        "backgroundPrompt": "",
        "openingRole": "旁白",
        "openingText": "",
    }
    
    # 提取背景图提示词
    bg_match = re.search(r"^## 章节背景图\s*\n提示词\s*\n```\s*(.+?)\s*```", content, re.DOTALL | re.MULTILINE)
    if bg_match:
        chapter_data["backgroundPrompt"] = bg_match.group(1).strip()
    
    # 提取章节内容（## 章节内容 ``` ... ```）
    content_match = re.search(r"^## 章节内容\s*\n```\s*(.*?)\s*```", content, re.DOTALL | re.MULTILINE)
    if content_match:
        chapter_data["content"] = content_match.group(1).strip()
    
    # 提取标题（第一个 # 标题）
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if title_match:
        chapter_data["title"] = title_match.group(1).strip()
    
    # 提取开场白（第一句旁白）
    narrator_match = re.search(r"@旁白[：:]\s*(.+?)(?=\n@|\n##|\Z)", content, re.DOTALL)
    if narrator_match:
        chapter_data["openingText"] = narrator_match.group(1).strip()[:200]
    
    return chapter_data


def get_world_data():
    """获取世界数据"""
    result = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if result.get("code") == 200:
        return result.get("data", {})
    raise Exception(f"获取世界失败: {result}")


def save_world(world_data):
    """保存世界数据"""
    world_data["worldId"] = world_data.get("id", WORLD_ID)
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    world_data["settings"] = settings
    result = api_call("/game/saveWorld", world_data)
    if result.get("code") == 200:
        print("✓ 世界保存成功")
        return result.get("data", {})
    else:
        print(f"✗ 世界保存失败: {result}")
        return None


def separate_avatar(avatar_path, role_name):
    """上传头像并进行人体分离"""
    print(f"  → 分离头像: {avatar_path.name}")

    with open(avatar_path, "rb") as f:
        img_data = f.read()
    base64_data = base64.b64encode(img_data).decode("utf-8")

    result = api_call("/game/separateRoleAvatar", {
        "worldId": WORLD_ID,
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
        print(f"  ✗ 分离失败: {result.get('message', str(result))}")
        return {}


def save_chapter(chapter_data):
    """保存章节"""
    chapter_data["worldId"] = WORLD_ID
    chapter_data["status"] = "draft"
    result = api_call("/game/saveChapter", chapter_data)
    if result.get("code") == 200:
        print(f"  ✓ 章节保存成功: {chapter_data.get('title', '')} (ID={result['data'].get('id')})")
        return result.get("data", {})
    else:
        print(f"  ✗ 章节保存失败: {result}")
        return None


def main():
    print("=" * 60)
    print("角色和章节数据更新 - ai_story/local")
    print("=" * 60)

    # 1. 获取当前世界数据
    print("\n[1/4] 获取世界数据...")
    world_data = get_world_data()
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    
    # 确保 roles 是列表
    if "roles" not in settings:
        settings["roles"] = []
    roles = settings["roles"]
    existing_role_map = {r.get("name"): r for r in roles}
    
    print(f"  当前角色数: {len(roles)}")
    print(f"  当前章节数: {len(world_data.get('chapters', []))}")

    # 2. 处理角色
    print("\n[2/4] 处理角色...")
    avatar_results = {}  # role_name -> avatar paths

    for role_name, md_file in ROLE_NAME_TO_FILE.items():
        md_path = ROLES_DIR / md_file
        if not md_path.exists():
            print(f"  ⚠ 跳过(文件不存在): {md_path}")
            continue

        print(f"\n  处理: {role_name}")
        
        # 解析 MD
        role_data = parse_md_role(md_path)
        print(f"    名称: {role_data.get('name', role_name)}")
        print(f"    描述长度: {len(role_data.get('description', ''))} 字符")
        
        # 处理头像分离
        avatar_file = ROLE_NAME_TO_AVATAR.get(role_name)
        avatar_path = AVATARS_DIR / avatar_file if avatar_file else None
        avatar_result = {}
        
        if avatar_path and avatar_path.exists():
            avatar_result = separate_avatar(avatar_path, role_name)
            if avatar_result:
                print(f"    前景: {avatar_result.get('avatarPath', '')[:60]}...")
        else:
            print(f"    ⚠ 头像文件不存在: {avatar_path}")
        
        avatar_results[role_name] = avatar_result
        
        # 构建角色对象
        role_obj = {
            "id": f"npc_{role_name}",  # 临时ID，服务器会分配真实ID
            "roleType": "npc",
            "name": role_data.get("name", role_name),
            "description": role_data.get("description", ""),
            "avatarImagePrompt": role_data.get("avatarImagePrompt", ""),
            "voiceMode": "prompt_voice",
            "voicePromptText": role_data.get("voicePromptText", ""),
            "parameterCardJson": role_data.get("parameterCardJson"),
        }
        # 添加头像路径
        role_obj.update(avatar_result)
        
        # 检查是否已存在
        if role_name in existing_role_map:
            # 更新现有角色
            existing = existing_role_map[role_name]
            for k, v in role_obj.items():
                if v and k != "id":  # 不覆盖ID
                    existing[k] = v
            print(f"    ✓ 更新现有角色")
        else:
            # 添加新角色
            roles.append(role_obj)
            print(f"    ✓ 添加新角色")
        
        # 记录音色提示词
        if role_data.get("voicePromptText"):
            print(f"    音色: {role_data['voicePromptText'][:50]}...")

    # 3. 保存世界（角色数据）
    print("\n[3/4] 保存世界数据...")
    settings["roles"] = roles
    world_data["settings"] = settings
    saved_world = save_world(world_data)
    
    # 更新角色映射（获取真实ID）
    if saved_world:
        saved_settings = saved_world.get("settings", {})
        if isinstance(saved_settings, str):
            saved_settings = json.loads(saved_settings)
        updated_roles = saved_settings.get("roles", [])
        existing_role_map = {r.get("name"): r for r in updated_roles}

    # 4. 处理章节
    print("\n[4/4] 处理章节...")
    if not CHAPTERS_DIR.exists():
        print("  ⚠ chapters 目录不存在")
    else:
        chapter_files = sorted(CHAPTERS_DIR.glob("*.md"))
        for i, chapter_file in enumerate(chapter_files):
            # 跳过非章节文件
            if chapter_file.stem in ["role.list", "README"]:
                continue
            
            print(f"\n  处理章节: {chapter_file.name}")
            chapter_data = parse_chapter_md(chapter_file)
            print(f"    标题: {chapter_data.get('title', '未命名')}")
            print(f"    内容长度: {len(chapter_data.get('content', ''))} 字符")
            print(f"    开场: {chapter_data.get('openingText', '')[:50]}...")
            
            # 如果有背景提示词
            if chapter_data.get("backgroundPrompt"):
                print(f"    背景提示词: {chapter_data['backgroundPrompt'][:50]}...")
            
            chapter_data["sort"] = i
            save_chapter(chapter_data)

    print(f"\n{'='*60}")
    print("更新完成!")
    print(f"角色数: {len(roles)}")
    print(f"章节数: {len(chapter_files) if CHAPTERS_DIR.exists() else 0}")


if __name__ == "__main__":
    main()