#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新服务器角色信息
读取本地角色md文件，解析角色设定，然后更新到服务器的world settings中
"""
import os
import re
import json
import requests
from pathlib import Path

# 配置
BASE_URL = "http://122.51.232.171:60002"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzc5OTEwMDA5LCJleHAiOjE3OTU0NjIwMDl9.FlDWRs9KmFo97rt9sob8emsQC5IXdVUZTlvC6wXCNL8"
WORLD_ID = 35
ROLES_DIR = Path("/ai_story/171/我的诡异表妹/roles")

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def get_world():
    """获取当前世界数据"""
    response = requests.post(f"{BASE_URL}/game/getWorld", json={"worldId": WORLD_ID}, headers=HEADERS, verify=False)
    response.raise_for_status()
    result = response.json()
    # API返回格式: {"code":200,"data":{...},"message":""}
    if result.get("code") == 200:
        return result.get("data", {})
    raise Exception(f"获取世界失败: {result}")


def save_world(world_data):
    """保存世界数据（更新）"""
    # 关键：必须传 worldId 才能更新，否则会创建新世界
    payload = {
        "worldId": world_data.get("id"),
        "projectId": world_data.get("projectId", 1),
        "name": world_data.get("name"),
        "intro": world_data.get("intro"),
        "coverPath": world_data.get("coverPath"),
        "publishStatus": world_data.get("publishStatus", "draft"),
        "settings": world_data.get("settings")
    }
    print(f"\n  发送 payload: worldId={payload['worldId']}, name={payload['name']}")
    try:
        response = requests.post(f"{BASE_URL}/game/saveWorld", json=payload, headers=HEADERS, verify=False)
        result = response.json()
        print(f"  响应: {result}")
        return result
    except requests.exceptions.HTTPError as e:
        print(f"  HTTP错误: {e}")
        print(f"  响应内容: {response.text}")
        raise


def parse_role_from_md(md_path):
    """解析md文件，提取角色设定"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    role_data = {
        "roleType": "npc",
        "attributes": {}
    }

    # 提取基本信息
    filename = md_path.stem
    # 处理特殊文件名
    if filename == "role.list":
        return None  # 跳过目录列表文件

    role_data["id"] = f"npc_{filename}"
    role_data["name"] = filename  # 用文件名作为默认名称

    # 从参数卡中获取实际角色名
    param_match = re.search(r'## 角色参数卡\s*\n```json\s*\n(.*?)\n```', content, re.DOTALL)
    if param_match:
        try:
            param_json = json.loads(param_match.group(1))
            if "name" in param_json:
                role_data["name"] = param_json["name"]
                # 特殊处理：文件名小七对应npc_xiaoqi
                if filename == "小七":
                    role_data["id"] = "npc_xiaoqi"
                elif filename == "用户":
                    role_data["id"] = "player"
                elif filename == "校长":
                    role_data["id"] = "npc_principal"
        except:
            pass

    # 提取角色设定部分
    match = re.search(r'## 角色设定.*?\n(.*?)(?=##|$)', content, re.DOTALL)
    if match:
        setting_text = match.group(1).strip()

        # 提取键值对
        key_patterns = [
            r'性别:\s*(.+)',
            r'年龄:\s*(.+)',
            r'性格:\s*(.+)',
            r'外貌:\s*(.+)',
            r'音色特点:\s*(.+)',
            r'技能:\s*(.+)',
            r'物品:\s*(.+)',
            r'装备:\s*(.+)',
            r'等级:\s*(.+)',
            r'血量:\s*(.+)',
            r'蓝量:\s*(.+)',
            r'金钱:\s*(.+)',
            r'其他:\s*(.+)',
        ]

        role_data["name"] = filename
        role_data["description"] = ""

        for pattern in key_patterns:
            kv_match = re.search(pattern, setting_text)
            if kv_match:
                key = pattern.split(':\\s*')[0]
                value = kv_match.group(1).strip()

                if key == "性别":
                    role_data["gender"] = value
                elif key == "年龄":
                    role_data["age"] = int(value) if value.isdigit() else value
                elif key == "性格":
                    role_data["personality"] = value
                elif key == "外貌":
                    role_data["appearance"] = value
                elif key == "音色特点":
                    role_data["voice_feature"] = value
                elif key == "技能":
                    role_data["skills"] = [s.strip() for s in value.split('，') if s.strip()]
                elif key == "物品":
                    role_data["items"] = [s.strip() for s in value.split('，') if s.strip()]
                elif key == "装备":
                    role_data["equipment"] = [s.strip() for s in value.split('，') if s.strip()]
                elif key == "等级":
                    role_data["level"] = int(value) if value.isdigit() else value
                elif key == "血量":
                    role_data["hp"] = int(value) if value.isdigit() else value
                elif key == "蓝量":
                    role_data["mp"] = int(value) if value.isdigit() else value
                elif key == "金钱":
                    role_data["money"] = int(value) if value.isdigit() else value
                elif key == "其他":
                    role_data["other"] = [s.strip() for s in value.split('，') if s.strip()]

        # 提取描述文字（键值对之前的文字）
        # 找到第一个键值对的位置
        first_kv_pos = len(setting_text)
        for pattern in key_patterns:
            kv_m = re.search(pattern, setting_text)
            if kv_m and kv_m.start() < first_kv_pos:
                first_kv_pos = kv_m.start()

        if first_kv_pos > 0:
            # 获取键值对之前的描述文字（去掉开头的换行）
            desc_text = setting_text[:first_kv_pos].strip()
            if desc_text:
                role_data["description"] = desc_text

    # 提取头像提示词
    avatar_match = re.search(r'## 头像.*?\n.*?前景[：:]\s*(.+?)(?:\n|$)', content, re.DOTALL)
    if avatar_match:
        role_data["avatarPrompt"] = avatar_match.group(1).strip()

    # 提取语音提示词
    voice_match = re.search(r'提示词[：:]\s*(.+?)(?:\n|$)', content, re.DOTALL)
    if voice_match:
        role_data["voicePromptText"] = voice_match.group(1).strip()

    # 提取语音模式
    mode_match = re.search(r'模式[：:]\s*(.+?)(?:\n|$)', content, re.DOTALL)
    if mode_match:
        role_data["voiceMode"] = mode_match.group(1).strip()

    # 提取角色参数卡
    param_match = re.search(r'## 角色参数卡\s*\n```json\s*\n(.*?)\n```', content, re.DOTALL)
    if param_match:
        try:
            role_data["parameterCardJson"] = json.loads(param_match.group(1))
        except:
            pass

    # 提取rawSetting
    raw_match = re.search(r'raw_setting["：:]\s*["\'](.+?)["\']', content, re.DOTALL)
    if raw_match:
        role_data["rawSetting"] = raw_match.group(1)

    return role_data


def main():
    print("=" * 60)
    print("开始更新服务器角色信息")
    print("=" * 60)

    # 1. 获取当前世界数据
    print("\n[1/4] 获取当前世界数据...")
    world = get_world()
    settings = world.get("settings", {})

    if isinstance(settings, str):
        settings = json.loads(settings)

    print(f"  世界ID: {world.get('id')}")
    print(f"  世界名称: {world.get('name')}")

    # 2. 读取本地角色文件
    print("\n[2/4] 读取本地角色文件...")
    role_files = list(ROLES_DIR.glob("*.md"))
    print(f"  找到 {len(role_files)} 个角色文件")

    # 解析所有角色
    local_roles = {}
    for md_file in role_files:
        role_name = md_file.stem
        print(f"  - 解析: {role_name}")
        try:
            role_data = parse_role_from_md(md_file)
            if role_data is None:
                print(f"    -> 跳过")
                continue
            role_id = role_data.get("id")
            local_roles[role_id] = role_data
            print(f"    -> ID: {role_id}")
        except Exception as e:
            print(f"    -> 错误: {e}")

    # 3. 更新settings中的roles
    print("\n[3/4] 更新角色数据...")

    existing_roles = settings.get("roles", [])
    updated_count = 0
    created_count = 0

    for role_id, new_role in local_roles.items():
        # 查找是否已存在该角色
        existing = None
        for i, r in enumerate(existing_roles):
            if r.get("id") == role_id:
                existing = i
                break

        role_entry = {
            "id": role_id,
            "roleType": "npc",
            "name": new_role.get("name", role_id.replace("npc_", "")),
            "description": new_role.get("description", ""),
            "attributes": {},
            "voiceMode": new_role.get("voiceMode", "prompt_voice"),
            "voice": "",
            "voicePromptText": new_role.get("voicePromptText", ""),
            "parameterCardJson": new_role.get("parameterCardJson", {}),
            "voiceMixVoices": [],
        }

        # 补充详细属性到parameterCardJson
        if "parameterCardJson" not in role_entry:
            role_entry["parameterCardJson"] = {}

        pc = role_entry["parameterCardJson"]
        pc["name"] = new_role.get("name", role_id.replace("npc_", ""))

        if "gender" in new_role:
            pc["gender"] = new_role["gender"]
        if "age" in new_role:
            pc["age"] = new_role["age"]
        if "level" in new_role:
            pc["level"] = new_role["level"]
        if "personality" in new_role:
            pc["personality"] = new_role["personality"]
        if "appearance" in new_role:
            pc["appearance"] = new_role["appearance"]
        if "skills" in new_role:
            pc["skills"] = new_role["skills"]
        if "items" in new_role:
            pc["items"] = new_role["items"]
        if "equipment" in new_role:
            pc["equipment"] = new_role["equipment"]
        if "hp" in new_role:
            pc["hp"] = new_role["hp"]
        if "mp" in new_role:
            pc["mp"] = new_role["mp"]
        if "money" in new_role:
            pc["money"] = new_role["money"]
        if "other" in new_role:
            pc["other"] = new_role["other"]
        if "rawSetting" in new_role:
            pc["raw_setting"] = new_role["rawSetting"]

        if existing is not None:
            existing_roles[existing] = role_entry
            updated_count += 1
            print(f"  更新: {role_id}")
        else:
            existing_roles.append(role_entry)
            created_count += 1
            print(f"  新增: {role_id}")

    settings["roles"] = existing_roles

    # 4. 保存到服务器
    print("\n[4/4] 保存到服务器...")
    world["settings"] = settings

    # 关键：确保有worldId
    if "worldId" not in world:
        world["worldId"] = world.get("id")

    result = save_world(world)
    print(f"  保存结果: {result}")

    print("\n" + "=" * 60)
    print(f"完成！更新 {updated_count} 个角色，新增 {created_count} 个角色")
    print("=" * 60)


if __name__ == "__main__":
    main()