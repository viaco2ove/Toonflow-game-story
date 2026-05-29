#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
角色数据全面更新脚本
任务：
1. 角色设定 - 从 MD 文件读取
2. avatarImagePrompt - 从 MD 文件提取
3. 头像上传和人体分离 - 上传本地头像 → separateRoleAvatar → 获取 sourcePath
4. 音色提示词和音色文件生成 - 从 MD 文件提取 → 调用 generateBindingVoice

然后调用 saveWorld 保存所有数据
"""

import requests
import json
import base64
import os
import re
from pathlib import Path

# 配置
BASE_URL = "http://122.51.232.171:60002"
TOKEN = "***REMOVED***"
PROJECT_ID = 1
WORLD_ID = 35

ROLES_DIR = Path("D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/171/我的诡异表妹/roles")
AVATARS_DIR = Path("D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/171/我的诡异表妹/avatars")

# 服务器角色真实ID映射（从 getWorld API 获取）
SERVER_ROLE_IDS = {
    "小七": "npc_xiaoqi",
    "用户": "npc_用户",
    "许飞": "npc_用户",
    "校长": "npc_xiaozhang",
    "苏老师": "npc_sulaoshi",
    "裂口女": "npc_liekounv",
    "无面人": "npc_wumianren",
    "长发女": "npc_changfany",
    "李明": "npc_liming",
    "王思远": "npc_wangsiyuan",
    "赵小胖": "npc_zhaoxiaopang",
    "路人甲": "npc_lurenjia",
}

# 角色名称到MD文件的映射
ROLE_NAME_TO_FILE = {
    "小七": "小七.md",
    "许飞": "用户.md",  # 用户/许飞 使用同一文件
    "校长": "校长.md",
    "苏老师": "诡异美女老师.md",
    "裂口女": "诡异A（裂口女）.md",
    "无面人": "诡异B（无面人）.md",
    "长发女": "诡异C（长发女）.md",
    "李明": "人类学生甲.md",
    "王思远": "人类学生乙.md",
    "赵小胖": "人类学生丙.md",
    "路人甲": "路人甲.md",
}

# 角色名称到头像文件的映射
ROLE_NAME_TO_AVATAR = {
    "小七": "xiaoqi.png",
    "苏老师": "sulaoshi.png",
    "校长": "xiaozhang.png",
    "裂口女": "liekounv.png",
    "无面人": "wumianren.png",
    "长发女": "changfanv.png",
    "李明": "liming.png",
    "王思远": "wangsiyuan.png",
    "赵小胖": "zhaoxiaopang.png",
    "路人甲": "lurenjia.png",
    "用户": "xufei.png",
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
        "voiceMode": "prompt_voice",
        "voicePromptText": "",
        "parameterCardJson": None,
    }

    # 提取基本信息
    name_match = re.search(r"- \*\*名称\*\*[：:]\s*(.+)", content)
    if name_match:
        role_data["name"] = name_match.group(1).strip()

    role_id_match = re.search(r"- \*\*角色ID\*\*[：:]\s*(.+)", content)
    if role_id_match:
        role_data["id"] = role_id_match.group(1).strip()

    # 提取角色设定（从 "## 角色设定" 到下一个 ## 之前）
    setting_match = re.search(r"## 角色设定.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if setting_match:
        role_data["description"] = setting_match.group(1).strip()

    # 提取头像生图描述（前景/背景）
    avatar_match = re.search(r"## 头像.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if avatar_match:
        avatar_section = avatar_match.group(1)
        # 提取前景描述
        fg_match = re.search(r"\*\*前景\*\*[：:]\s*(.+?)(?=\n\s*[-*]|\n##|\Z)", avatar_section, re.DOTALL)
        if fg_match:
            role_data["avatarPrompt"] = fg_match.group(1).strip()
            role_data["avatarImagePrompt"] = fg_match.group(1).strip()
        # 提取背景描述
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


def get_world_data():
    """获取世界数据"""
    result = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if result.get("code") == 200:
        return result.get("data", {})
    raise Exception(f"获取世界失败: {result}")


def update_world_roles(updates):
    """更新世界角色数据并保存"""
    world_data = get_world_data()
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)

    roles = settings.get("roles", [])
    role_map = {r.get("id"): r for r in roles}

    # 更新角色数据
    for update in updates:
        role_id = update.get("id")
        if role_id in role_map:
            role = role_map[role_id]
            # 只更新指定字段，保留其他字段
            for key, value in update.items():
                if value and key != "id":
                    role[key] = value
            print(f"  ✓ 更新角色: {update.get('name', role_id)}")
        else:
            print(f"  ✗ 角色未找到: {role_id}")

    # 保存世界
    world_data["worldId"] = world_data.get("id")
    world_data["settings"] = settings
    save_result = api_call("/game/saveWorld", world_data)
    if save_result.get("code") == 200:
        print("✓ 世界保存成功")
    else:
        print(f"✗ 世界保存失败: {save_result}")


def separate_avatar(role_id, avatar_path):
    """上传头像并进行人体分离"""
    print(f"  → 上传并分离: {avatar_path.name}")

    # 读取图片并转 base64
    with open(avatar_path, "rb") as f:
        img_data = f.read()
    base64_data = base64.b64encode(img_data).decode("utf-8")

    # 调用分离接口
    result = api_call("/game/separateRoleAvatar", {
        "roleId": role_id,
        "base64Data": base64_data
    })

    if result.get("code") == 200:
        data = result.get("data", {})
        return {
            "avatarSourcePath": data.get("sourceFilePath", ""),
            "avatarPath": data.get("foregroundFilePath", ""),
            "avatarBgPath": data.get("backgroundFilePath", ""),
        }
    else:
        print(f"  ✗ 分离失败: {result.get('message', result)}")
        return {}


def generate_voice(role_id, voice_prompt_text, config_id=27):
    """生成音色"""
    print(f"  → 生成音色...")

    result = api_call("/voice/generateBindingVoice", {
        "configId": config_id,
        "roleId": role_id,
        "mode": "prompt_voice",
        "voiceId": "",
        "referenceAudioPath": "",
        "referenceText": "",
        "promptText": voice_prompt_text,
        "mixVoices": []
    })

    if result.get("code") == 200:
        data = result.get("data", {})
        return {
            "voiceReferenceAudioPath": data.get("audioPath", ""),
            "voicePresetId": data.get("customVoiceId", ""),
        }
    else:
        print(f"  ✗ 音色生成失败: {result.get('message', result)}")
        return {}


def main():
    print("=" * 60)
    print("角色数据全面更新")
    print("=" * 60)

    # 获取当前世界角色数据
    world_data = get_world_data()
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    roles = settings.get("roles", [])
    server_role_map = {r.get("name"): r for r in roles}

    all_updates = []

    # 遍历所有角色
    for role_name, md_file in ROLE_NAME_TO_FILE.items():
        md_path = ROLES_DIR / md_file
        if not md_path.exists():
            print(f"\n[跳过] 文件不存在: {md_path}")
            continue

        print(f"\n{'='*50}")
        print(f"处理角色: {role_name}")

        # 1. 解析 MD 文件
        role_data = parse_md_role(md_path)
        
        # 使用服务器真实ID
        role_id = SERVER_ROLE_IDS.get(role_name)
        if not role_id:
            print(f"  ✗ 无法获取角色ID，跳过")
            continue

        print(f"  角色ID: {role_id}")

        # 2. 分离头像
        avatar_file = ROLE_NAME_TO_AVATAR.get(role_name)
        avatar_path = AVATARS_DIR / avatar_file if avatar_file else None
        avatar_update = {}

        if avatar_path and avatar_path.exists():
            avatar_update = separate_avatar(role_id, avatar_path)
        else:
            print(f"  ⚠ 头像文件不存在: {avatar_path}")

        # 3. 生成音色
        voice_prompt = role_data.get("voicePromptText", "")
        voice_update = {}
        if voice_prompt:
            voice_update = generate_voice(role_id, voice_prompt)
        else:
            print(f"  ⚠ 无音色提示词")

        # 4. 汇总更新
        update = {
            "id": role_id,
            "name": role_data.get("name", role_name),
            "description": role_data.get("description", ""),
            "avatarImagePrompt": role_data.get("avatarImagePrompt", ""),
            "avatarPrompt": role_data.get("avatarPrompt", ""),
            "avatarBgPrompt": role_data.get("avatarBgPrompt", ""),
            "voiceMode": "prompt_voice",
            "voicePromptText": voice_prompt,
        }
        # 合并头像和音色数据
        update.update(avatar_update)
        update.update(voice_update)

        all_updates.append(update)

    # 5. 更新世界数据
    print(f"\n{'='*50}")
    print("更新世界数据...")
    update_world_roles(all_updates)

    print(f"\n{'='*50}")
    print("完成!")


if __name__ == "__main__":
    main()