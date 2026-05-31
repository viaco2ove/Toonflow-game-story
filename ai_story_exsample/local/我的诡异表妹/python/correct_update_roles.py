#!/usr/bin/env python3
"""
正确流程的角色更新脚本：
1. 上传本地头像 → separateRoleAvatar 分离
2. 生成音色文件
3. saveWorld 时直接添加 avatarImagePrompt
4. 更新角色设定
"""
import os
import json
import re
import glob
import base64
import urllib.request, urllib.error

BASE_URL = "http://122.51.232.171:60002"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzc5OTEwMDA5LCJleHAiOjE3OTU0NjIwMDl9.FlDWRs9KmFo97rt9sob8emsQC5IXdVUZTlvC6wXCNL8"
WORLD_ID = 35
PROJECT_ID = 1

ROLES_DIR = r"/ai_story/171/我的诡异表妹/roles"
AVATARS_DIR = r"/ai_story/171/我的诡异表妹/avatars"

# 角色名称到文件名的映射
ROLE_NAME_MAP = {
    "小七": "xiaoqi.png",
    "校长": "xiaozhang.png",
    "苏老师": "sulaoshi.png",
    "裂口女": "liekounv.png",
    "无面人": "wumianren.png",
    "长发女": "changfanv.png",
    "李明": "liming.png",
    "王思远": "wangsiyuan.png",
    "赵小胖": "zhaoxiaopang.png",
    "路人甲": "lurenjia.png",
    "用户": None,  # 玩家角色，不需要上传头像
    "旁白": None,  # 旁白角色，不需要上传头像
}

def api_call(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
            return {"code": e.code, "message": str(e), "body": error_body}
        except:
            return {"code": e.code, "message": str(e)}
    except Exception as e:
        return {"code": 500, "message": str(e)}

def parse_md_file(md_path):
    """解析MD文件，提取角色信息"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取角色ID
    role_id_match = re.search(r'\*\*角色ID\*\*[：:]\s*(\S+)', content)
    role_id = role_id_match.group(1) if role_id_match else None
    
    # 提取角色名称
    name_match = re.search(r'\*\*名称\*\*[：:]\s*(.+)', content)
    name = name_match.group(1).strip() if name_match else os.path.splitext(os.path.basename(md_path))[0]
    
    # 提取角色类型
    type_match = re.search(r'\*\*角色类型\*\*[：:]\s*(\S+)', content)
    role_type = type_match.group(1) if type_match else "npc"
    
    # 提取角色设定
    desc_match = re.search(r'## 角色设定.*?\n(.+?)(?=##|\n---\n|$)', content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    
    # 提取头像AI生图提示词（前景）
    avatar_prompt_match = re.search(r'- \*\*前景\*\*[：:]\s*(.+?)(?=\n-|##|\n---\n|$)', content, re.DOTALL)
    avatar_image_prompt = avatar_prompt_match.group(1).strip() if avatar_prompt_match else ""
    
    # 提取背景提示词
    bg_prompt_match = re.search(r'- \*\*背景\*\*[：:]\s*(.+?)(?=\n-|##|\n---\n|$)', content, re.DOTALL)
    avatar_bg_prompt = bg_prompt_match.group(1).strip() if bg_prompt_match else ""
    
    # 提取语音提示词
    voice_prompt_match = re.search(r'- \*\*提示词\*\*[：:]\s*(.+?)(?=\n-|\n##|\n---\n|$)', content, re.DOTALL)
    voice_prompt_text = voice_prompt_match.group(1).strip() if voice_prompt_match else ""
    
    # 提取语音模式
    voice_mode_match = re.search(r'- \*\*模式\*\*[：:]\s*(\S+)', content)
    voice_mode = voice_mode_match.group(1) if voice_mode_match else "prompt_voice"
    
    # 提取参数卡JSON
    json_match = re.search(r'```json\s*([\s\S]+?)\s*```', content)
    parameter_card = {}
    if json_match:
        try:
            parameter_card = json.loads(json_match.group(1))
        except:
            pass
    
    return {
        "id": role_id,
        "name": name,
        "roleType": role_type,
        "description": description,
        "avatarImagePrompt": avatar_image_prompt,
        "avatarBgPrompt": avatar_bg_prompt,
        "voiceMode": voice_mode,
        "voicePromptText": voice_prompt_text,
        "parameterCardJson": parameter_card
    }

def upload_image(file_path):
    """上传图片到服务器"""
    if not os.path.exists(file_path):
        print(f"  文件不存在: {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        image_data = f.read()
    
    # 构建 multipart/form-data 请求
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\nContent-Type: image/png\r\n\r\n'
    body = body.encode('utf-8') + image_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    url = f"{BASE_URL}/game/uploadImage"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 200:
                return result.get("data", {}).get("path", "")
            return None
    except Exception as e:
        print(f"  上传失败: {e}")
        return None

def separate_role_avatar(role_id, image_path):
    """分离角色头像"""
    result = api_call("/game/separateRoleAvatar", {
        "roleId": role_id,
        "imagePath": image_path
    })
    if result.get("code") == 200:
        data = result.get("data", {})
        return {
            "avatarPath": data.get("avatarPath", ""),
            "avatarBgPath": data.get("avatarBgPath", ""),
            "avatarUrl": data.get("avatarUrl", ""),
            "avatarSourcePath": image_path  # 原始上传路径
        }
    print(f"  分离失败: {result.get('message')}")
    return None

def generate_voice(role_id, voice_mode, voice_prompt_text):
    """生成音色"""
    if not voice_prompt_text:
        print(f"  无语音提示词，跳过")
        return None
    
    data = {
        "roleId": role_id,
        "mode": voice_mode,
        "promptText": voice_prompt_text
    }
    
    result = api_call("/voice/generateBindingVoice", data)
    if result.get("code") == 200:
        data = result.get("data", {})
        return {
            "voiceId": data.get("voiceId", ""),
            "audioPath": data.get("audioPath", ""),
            "customVoiceId": data.get("customVoiceId", "")
        }
    print(f"  音色生成失败: {result.get('message')}")
    return None

def main():
    print("="*60)
    print("开始角色更新流程")
    print("="*60)
    
    # Step 1: 获取当前世界数据
    print("\n[Step 1] 获取世界数据...")
    world_result = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if world_result.get("code") != 200:
        print(f"获取世界失败: {world_result}")
        return
    world_data = world_result.get("data", {})
    
    # 解析 settings
    settings = world_data.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    if not isinstance(settings, dict):
        settings = {}
    
    # 获取现有角色列表
    existing_roles = settings.get("roles", [])
    existing_role_map = {}
    for role in existing_roles:
        if isinstance(role, dict):
            existing_role_map[role.get("id")] = role
    
    print(f"  现有角色数: {len(existing_role_map)}")
    
    # Step 2: 解析所有角色MD文件
    print("\n[Step 2] 解析角色文件...")
    md_files = glob.glob(os.path.join(ROLES_DIR, "*.md"))
    role_updates = []
    
    for md_path in md_files:
        role_info = parse_md_file(md_path)
        role_name = role_info["name"]
        
        if role_name in ["用户", "旁白"]:
            print(f"  跳过 {role_name} (无需处理)")
            continue
        
        if not role_info["id"]:
            print(f"  跳过 {role_name} (无角色ID)")
            continue
        
        print(f"  处理: {role_name} ({role_info['id']})")
        
        update_data = {
            "id": role_info["id"],
            "name": role_name,
            "roleType": role_info.get("roleType", "npc"),
            "description": role_info.get("description", ""),
            "avatarImagePrompt": role_info.get("avatarImagePrompt", ""),
            "avatarBgPrompt": role_info.get("avatarBgPrompt", ""),
            "voiceMode": role_info.get("voiceMode", "prompt_voice"),
            "voicePromptText": role_info.get("voicePromptText", ""),
            "parameterCardJson": role_info.get("parameterCardJson", {})
        }
        
        # Step 3: 上传头像并分离
        avatar_file = ROLE_NAME_MAP.get(role_name)
        if avatar_file:
            avatar_path = os.path.join(AVATARS_DIR, avatar_file)
            if os.path.exists(avatar_path):
                print(f"  上传头像: {avatar_file}")
                uploaded_path = upload_image(avatar_path)
                if uploaded_path:
                    print(f"    上传成功: {uploaded_path}")
                    print(f"  分离头像...")
                    sep_result = separate_role_avatar(role_info["id"], uploaded_path)
                    if sep_result:
                        update_data["avatarPath"] = sep_result.get("avatarPath", "")
                        update_data["avatarBgPath"] = sep_result.get("avatarBgPath", "")
                        update_data["avatarUrl"] = sep_result.get("avatarUrl", "")
                        update_data["avatarSourcePath"] = sep_result.get("avatarSourcePath", "")
                        print(f"    分离成功!")
                    else:
                        update_data["avatarSourcePath"] = uploaded_path
                else:
                    # 如果上传失败，尝试使用已有路径
                    existing = existing_role_map.get(role_info["id"], {})
                    if existing.get("avatarPath"):
                        update_data["avatarPath"] = existing.get("avatarPath")
                        update_data["avatarBgPath"] = existing.get("avatarBgPath")
                        update_data["avatarSourcePath"] = existing.get("avatarSourcePath", "")
                        print(f"    使用已有头像")
            else:
                print(f"    头像文件不存在: {avatar_path}")
        else:
            print(f"    无头像映射")
        
        # Step 4: 生成音色
        if role_info.get("voicePromptText"):
            print(f"  生成音色...")
            voice_result = generate_voice(
                role_info["id"],
                role_info.get("voiceMode", "prompt_voice"),
                role_info.get("voicePromptText", "")
            )
            if voice_result:
                update_data["voice"] = voice_result.get("audioPath", "")
                update_data["voiceId"] = voice_result.get("voiceId", "")
                update_data["customVoiceId"] = voice_result.get("customVoiceId", "")
                print(f"    音色生成成功!")
            else:
                # 使用已有音色
                existing = existing_role_map.get(role_info["id"], {})
                if existing.get("voice"):
                    update_data["voice"] = existing.get("voice")
                    print(f"    使用已有音色")
        else:
            print(f"  无语音提示词，跳过音色生成")
        
        role_updates.append(update_data)
    
    # Step 5: 更新世界数据
    print("\n[Step 5] 更新世界数据...")
    
    # 构建角色更新映射
    roles_to_update = {}
    for role in role_updates:
        roles_to_update[role["id"]] = role
    
    # 合并到现有角色
    updated_roles = []
    for role in existing_roles:
        if isinstance(role, dict):
            rid = role.get("id")
            if rid in roles_to_update:
                # 更新现有角色
                updated = {**role, **roles_to_update[rid]}
                # 移除不需要的字段
                updated.pop("voiceId", None)
                updated.pop("customVoiceId", None)
                updated_roles.append(updated)
            else:
                updated_roles.append(role)
    
    # 添加新角色（如果settings中没有）
    for role_id, role_data in roles_to_update.items():
        if not any(r.get("id") == role_id for r in updated_roles):
            role_data_copy = {k: v for k, v in role_data.items() if k not in ["voiceId", "customVoiceId"]}
            updated_roles.append(role_data_copy)
    
    # 更新 settings
    settings["roles"] = updated_roles
    
    # 构建保存数据
    save_data = {
        "worldId": world_data.get("id", WORLD_ID),
        "projectId": PROJECT_ID,
        "name": world_data.get("name", "我的诡异表妹"),
        "intro": world_data.get("intro", ""),
        "coverPath": world_data.get("coverPath", ""),
        "publishStatus": world_data.get("publishStatus", "draft"),
        "settings": settings,
        "playerRole": world_data.get("playerRole", {}),
        "narratorRole": world_data.get("narratorRole", {})
    }
    
    print(f"  更新角色数: {len(updated_roles)}")
    
    # 保存世界
    result = api_call("/game/saveWorld", save_data)
    if result.get("code") == 200:
        print(f"  保存成功!")
        print(f"  世界ID: {result.get('data', {}).get('id')}")
    else:
        print(f"  保存失败: {result.get('message')}")
    
    print("\n" + "="*60)
    print("更新完成!")
    print("="*60)

if __name__ == "__main__":
    main()