#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整更新角色到服务器
1. 角色设定
2. AI生图形象描述 -> 生成头像
3. 头像上传和人体分离
4. 音色提示词 -> 音色文件生成
"""
import os
import re
import json
import requests
import base64
import time
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
BASE_URL = "http://122.51.232.171:60002"
AUTH_TOKEN = "***REMOVED***"
PROJECT_ID = 1
WORLD_ID = 35
ROLES_DIR = Path("/ai_story/171/我的诡异表妹/roles")

HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}

def parse_role_md(md_path):
    """解析md文件"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = md_path.stem
    if filename == "role.list" or filename == "img":
        return None
    
    role = {
        "id": f"npc_{filename}",
        "name": filename,
        "role_setting": "",
        "avatar_prompt": "",
        "avatar_bg_prompt": "",
        "voice_prompt_text": "",
        "voice_mode": "prompt_voice",
        "parameter_card": {}
    }
    
    # 特殊角色ID映射
    id_map = {
        "小七": "npc_xiaoqi",
        "用户": "player",
        "校长": "npc_xiaozhang",
        "诡异A（裂口女）": "npc_诡异A（裂口女）",
        "诡异B（无面人）": "npc_诡异B（无面人）",
        "诡异C（长发女）": "npc_诡异C（长发女）",
        "诡异美女老师": "npc_诡异美女老师",
        "人类学生甲": "npc_人类学生甲",
        "人类学生乙": "npc_人类学生乙",
        "人类学生丙": "npc_人类学生丙",
        "路人甲": "npc_路人甲",
    }
    if filename in id_map:
        role["id"] = id_map[filename]
    
    # 提取角色设定
    match = re.search(r'## 角色设定\(.*?\n(.*?)(?=##\s*角色参数卡|$)', content, re.DOTALL)
    if match:
        role["role_setting"] = match.group(1).strip()
    
    # 提取ai生图描述
    avatar_match = re.search(r'## 头像\(.*?\n(.*?)(?=##\s*语音|$)', content, re.DOTALL)
    if avatar_match:
        avatar_section = avatar_match.group(1)
        fg_match = re.search(r'\*\*前景\*\*[：:]\s*(.+?)(?:\n|$)', avatar_section)
        if fg_match:
            role["avatar_prompt"] = fg_match.group(1).strip()
        bg_match = re.search(r'\*\*背景\*\*[：:]\s*(.+?)(?:\n|$)', avatar_section)
        if bg_match:
            role["avatar_bg_prompt"] = bg_match.group(1).strip()
    
    # 提取音色提示词
    voice_match = re.search(r'## 语音.*?\*\*提示词\*\*[：:]\s*(.+?)(?:\n|$)', content, re.DOTALL)
    if voice_match:
        role["voice_prompt_text"] = voice_match.group(1).strip()
    
    # 提取参数卡
    param_match = re.search(r'## 角色参数卡\s*\n```json\s*\n(.*?)\n```', content, re.DOTALL)
    if param_match:
        try:
            role["parameter_card"] = json.loads(param_match.group(1))
        except:
            pass
    
    return role


def get_world():
    """获取当前世界数据"""
    response = requests.post(f"{BASE_URL}/game/getWorld", json={"worldId": WORLD_ID}, headers=HEADERS, verify=False)
    result = response.json()
    if result.get("code") == 200:
        return result.get("data", {})
    raise Exception(f"获取世界失败: {result}")


def generate_image(role):
    """生成角色头像"""
    if not role["avatar_prompt"]:
        print(f"  ⏭️ {role['name']}: 无头像提示词，跳过生图")
        return None
    
    print(f"  🎨 {role['name']}: 生成头像...")
    payload = {
        "projectId": PROJECT_ID,
        "type": "role",
        "prompt": role["avatar_prompt"],
        "name": role["id"],
        "base64List": [],
        "size": "2K"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/game/generateImage", json=payload, headers=HEADERS, verify=False)
        result = response.json()
        if result.get("code") == 200:
            data = result.get("data", {})
            image_path = data.get("imagePath", "")
            print(f"  ✅ {role['name']}: 头像生成成功 -> {image_path}")
            return image_path
        else:
            print(f"  ❌ {role['name']}: 头像生成失败 -> {result}")
            return None
    except Exception as e:
        print(f"  ❌ {role['name']}: 头像生成异常 -> {e}")
        return None


def separate_avatar(role, image_path):
    """分离人体和背景"""
    if not image_path:
        print(f"  ⏭️ {role['name']}: 无头像路径，跳过分离")
        return None, None
    
    print(f"  🔀 {role['name']}: 分离人体和背景...")
    
    # 下载图片并转base64
    try:
        full_url = f"{BASE_URL.replace(':60002', '')}{image_path}" if not image_path.startswith('http') else image_path
        img_response = requests.get(full_url, verify=False, timeout=30)
        img_data = base64.b64encode(img_response.content).decode('utf-8')
        mime_type = 'image/jpeg' if image_path.endswith('.jpg') else 'image/png'
        base64_data = f"data:{mime_type};base64,{img_data}"
    except Exception as e:
        print(f"  ❌ {role['name']}: 下载图片失败 -> {e}")
        return None, None
    
    # 调用分离接口
    payload = {
        "projectId": PROJECT_ID,
        "fileName": f"{role['id']}_avatar.jpg",
        "name": role["id"],
        "base64Data": base64_data,
        "asyncTask": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/game/separateRoleAvatar", json=payload, headers=HEADERS, verify=False)
        result = response.json()
        if result.get("code") == 200:
            task_id = result.get("data", {}).get("taskId")
            print(f"  ⏳ {role['name']}: 分离任务已提交, taskId={task_id}")
            
            # 轮询分离进度
            for i in range(30):
                time.sleep(2)
                status_resp = requests.post(f"{BASE_URL}/game/separateRoleAvatar/status", 
                                        json={"taskId": task_id}, headers=HEADERS, verify=False)
                status_data = status_resp.json()
                if status_data.get("code") == 200:
                    task_status = status_data.get("data", {}).get("status")
                    if task_status == "completed":
                        avatar_path = status_data.get("data", {}).get("avatarPath")
                        avatar_bg_path = status_data.get("data", {}).get("avatarBgPath")
                        print(f"  ✅ {role['name']}: 分离完成 -> 前景={avatar_path}")
                        return avatar_path, avatar_bg_path
                    elif task_status == "failed":
                        print(f"  ❌ {role['name']}: 分离失败")
                        return None, None
                    else:
                        print(f"  ⏳ {role['name']}: 分离中... ({i+1}/30)")
                else:
                    break
            
            print(f"  ⏭️ {role['name']}: 分离超时，使用原图")
            return image_path, None
        else:
            print(f"  ❌ {role['name']}: 分离请求失败 -> {result}")
            return image_path, None
    except Exception as e:
        print(f"  ❌ {role['name']}: 分离异常 -> {e}")
        return image_path, None


def generate_voice(role):
    """生成音色"""
    if not role["voice_prompt_text"]:
        print(f"  ⏭️ {role['name']}: 无音色提示词，跳过")
        return None
    
    print(f"  🔊 {role['name']}: 生成音色...")
    payload = {
        "configId": 27,  # 使用默认configId
        "roleId": role["id"],
        "mode": role["voice_mode"],
        "voiceId": "",
        "referenceAudioPath": "",
        "referenceText": "",
        "promptText": role["voice_prompt_text"],
        "mixVoices": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/voice/generateBindingVoice", json=payload, headers=HEADERS, verify=False)
        result = response.json()
        if result.get("code") == 200:
            data = result.get("data", {})
            audio_path = data.get("audioPath", "")
            custom_voice_id = data.get("customVoiceId", "")
            print(f"  ✅ {role['name']}: 音色生成成功 -> {audio_path}")
            return audio_path
        else:
            print(f"  ❌ {role['name']}: 音色生成失败 -> {result}")
            return None
    except Exception as e:
        print(f"  ❌ {role['name']}: 音色生成异常 -> {e}")
        return None


def save_world(world_data, roles_data):
    """保存世界数据"""
    payload = {
        "worldId": world_data.get("id"),
        "projectId": world_data.get("projectId", 1),
        "name": world_data.get("name"),
        "intro": world_data.get("intro"),
        "coverPath": world_data.get("coverPath"),
        "publishStatus": world_data.get("publishStatus", "draft"),
        "settings": world_data.get("settings")
    }
    
    try:
        response = requests.post(f"{BASE_URL}/game/saveWorld", json=payload, headers=HEADERS, verify=False)
        result = response.json()
        return result
    except Exception as e:
        print(f"  ❌ 保存失败: {e}")
        raise


def main():
    print("=" * 60)
    print("完整更新角色到服务器")
    print("1. 角色设定")
    print("2. AI生图形象描述 -> 生成头像")
    print("3. 头像上传和人体分离")
    print("4. 音色提示词 -> 音色文件生成")
    print("=" * 60)
    
    # 1. 获取当前世界数据
    print("\n[1/5] 获取当前世界数据...")
    world = get_world()
    settings = world.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    print(f"  ✅ 世界ID: {world.get('id')}, 名称: {world.get('name')}")
    
    # 2. 读取本地角色文件
    print("\n[2/5] 读取本地角色文件...")
    local_roles = {}
    for md_file in ROLES_DIR.glob("*.md"):
        role = parse_role_md(md_file)
        if role:
            local_roles[role["id"]] = role
            print(f"  ✅ {role['name']} ({role['id']})")
    print(f"  共 {len(local_roles)} 个角色")
    
    # 3. 为每个角色生成头像
    print("\n[3/5] AI生图生成头像...")
    image_results = {}
    for role_id, role in local_roles.items():
        image_path = generate_image(role)
        image_results[role_id] = image_path
    
    # 4. 分离人体和背景
    print("\n[4/5] 分离人体和背景...")
    avatar_results = {}
    for role_id, role in local_roles.items():
        image_path = image_results.get(role_id)
        if image_path:
            avatar_path, avatar_bg_path = separate_avatar(role, image_path)
            avatar_results[role_id] = {"avatarPath": avatar_path, "avatarBgPath": avatar_bg_path}
        else:
            avatar_results[role_id] = {"avatarPath": None, "avatarBgPath": None}
    
    # 5. 生成音色
    print("\n[5/5] 生成音色...")
    voice_results = {}
    for role_id, role in local_roles.items():
        audio_path = generate_voice(role)
        voice_results[role_id] = audio_path
    
    # 6. 更新服务器角色数据
    print("\n[6/6] 更新服务器角色数据...")
    existing_roles = settings.get("roles", [])
    
    for role_id, new_role in local_roles.items():
        # 查找已存在角色
        existing_idx = None
        for i, r in enumerate(existing_roles):
            if r.get("id") == role_id:
                existing_idx = i
                break
        
        # 构建角色数据
        pc = new_role.get("parameter_card", {})
        pc["name"] = new_role["name"]
        
        role_entry = {
            "id": role_id,
            "roleType": "npc",
            "name": new_role["name"],
            "description": new_role["role_setting"],
            "attributes": {},
            "voiceMode": new_role["voice_mode"],
            "voice": voice_results.get(role_id, ""),
            "voicePromptText": new_role["voice_prompt_text"],
            "parameterCardJson": pc,
            "voiceMixVoices": [],
        }
        
        # 添加头像路径
        avatar_data = avatar_results.get(role_id, {})
        if avatar_data.get("avatarPath"):
            role_entry["avatarPath"] = avatar_data["avatarPath"]
        if avatar_data.get("avatarBgPath"):
            role_entry["avatarBgPath"] = avatar_data["avatarBgPath"]
        
        if existing_idx is not None:
            existing_roles[existing_idx] = role_entry
            print(f"  🔄 {new_role['name']}: 已更新")
        else:
            existing_roles.append(role_entry)
            print(f"  🆕 {new_role['name']}: 新增")
    
    settings["roles"] = existing_roles
    world["settings"] = settings
    
    print("\n保存到服务器...")
    result = save_world(world, existing_roles)
    print(f"  结果: {result}")
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()