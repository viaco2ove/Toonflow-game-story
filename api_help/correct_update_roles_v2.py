#!/usr/bin/env python3
"""
正确流程的角色更新脚本：
1. 本地图片 base64 → separateRoleAvatar 分离
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
TOKEN = "***REMOVED***"
WORLD_ID = 35
PROJECT_ID = 1

ROLES_DIR = r"D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story\ai_story\171\我的诡异表妹\roles"
AVATARS_DIR = r"D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story\ai_story\171\我的诡异表妹\avatars"

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
    "用户": None,  # 玩家角色
    "旁白": None,  # 旁白角色
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
        with urllib.request.urlopen(req, timeout=60) as resp:
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

def separate_role_avatar_base64(role_id, image_path, image_bytes):
    """用 base64 方式分离角色头像"""
    # 检测图片类型
    if image_path.lower().endswith('.png'):
        mime_type = "image/png"
    else:
        mime_type = "image/jpeg"
    
    # 转换为 base64
    b64_data = base64.b64encode(image_bytes).decode('utf-8')
    b64_str = f"data:{mime_type};base64,{b64_data}"
    
    # 生成文件名
    file_name = os.path.basename(image_path)
    
    result = api_call("/game/separateRoleAvatar", {
        "projectId": PROJECT_ID,
        "roleId": role_id,
        "fileName": file_name,
        "base64Data": b64_str,
        "asyncTask": True
    })
    
    if result.get("code") == 200:
        data = result.get("data", {})
        task_id = data.get("taskId")
        if task_id:
            # 轮询任务状态
            return wait_for_separation(task_id, role_id)
        else:
            # 直接返回结果（同步模式）
            return {
                "avatarPath": data.get("avatarPath", ""),
                "avatarBgPath": data.get("avatarBgPath", ""),
                "avatarUrl": data.get("avatarUrl", ""),
                "avatarSourcePath": ""
            }
    
    print(f"  分离请求失败: {result.get('message')}")
    if "body" in result:
        print(f"  详情: {result['body'][:500]}")
    return None

def wait_for_separation(task_id, role_id, max_wait=60):
    """等待头像分离任务完成"""
    import time
    for i in range(max_wait):
        result = api_call("/game/separateRoleAvatar/status", {"taskId": task_id})
        if result.get("code") == 200:
            data = result.get("data", {})
            status = data.get("status")
            if status == "completed":
                return {
                    "avatarPath": data.get("avatarPath", ""),
                    "avatarBgPath": data.get("avatarBgPath", ""),
                    "avatarUrl": data.get("avatarUrl", ""),
                    "avatarSourcePath": data.get("sourcePath", "")
                }
            elif status == "failed":
                print(f"  分离任务失败")
                return None
        time.sleep(1)
        if i % 10 == 0:
            print(f"  等待分离完成... ({i}s)")
    print(f"  分离超时")
    return None

def generate_voice(role_id, voice_mode, voice_prompt_text, config_id=27):
    """生成音色"""
    if not voice_prompt_text:
        print(f"  无语音提示词，跳过")
        return None
    
    data = {
        "configId": config_id,
        "roleId": role_id,
        "mode": voice_mode,
        "voiceId": "",
        "referenceAudioPath": "",
        "referenceText": "",
        "promptText": voice_prompt_text,
        "mixVoices": []
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
    if "body" in result:
        print(f"  详情: {result['body'][:500]}")
    return None

def main():
    print("="*60)
    print("开始角色更新流程（正确版）")
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
        
        print(f"\n  === 处理: {role_name} ({role_info['id']}) ===")
        
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
        
        # Step 3: base64 方式上传并分离头像
        avatar_file = ROLE_NAME_MAP.get(role_name)
        if avatar_file:
            avatar_path = os.path.join(AVATARS_DIR, avatar_file)
            if os.path.exists(avatar_path):
                print(f"  读取头像: {avatar_file}")
                with open(avatar_path, 'rb') as f:
                    image_bytes = f.read()
                
                print(f"  分离头像（base64方式）...")
                sep_result = separate_role_avatar_base64(role_info["id"], avatar_path, image_bytes)
                if sep_result:
                    update_data["avatarPath"] = sep_result.get("avatarPath", "")
                    update_data["avatarBgPath"] = sep_result.get("avatarBgPath", "")
                    update_data["avatarUrl"] = sep_result.get("avatarUrl", "")
                    update_data["avatarSourcePath"] = sep_result.get("avatarSourcePath", "")
                    print(f"    分离成功!")
                    if update_data.get("avatarPath"):
                        print(f"    avatarPath: {update_data['avatarPath']}")
                else:
                    # 使用已有头像
                    existing = existing_role_map.get(role_info["id"], {})
                    update_data["avatarPath"] = existing.get("avatarPath", "")
                    update_data["avatarBgPath"] = existing.get("avatarBgPath", "")
                    update_data["avatarSourcePath"] = existing.get("avatarSourcePath", "")
                    print(f"    使用已有头像")
            else:
                print(f"    头像文件不存在: {avatar_path}")
        else:
            print(f"    无头像映射，使用已有头像")
            existing = existing_role_map.get(role_info["id"], {})
            update_data["avatarPath"] = existing.get("avatarPath", "")
            update_data["avatarBgPath"] = existing.get("avatarBgPath", "")
            update_data["avatarSourcePath"] = existing.get("avatarSourcePath", "")
        
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
                if update_data.get("voice"):
                    print(f"    voice: {update_data['voice']}")
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
    print("\n" + "="*60)
    print("[Step 5] 更新世界数据...")
    
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
        if "body" in result:
            print(f"  详情: {result['body'][:500]}")
    
    print("\n" + "="*60)
    print("更新完成!")
    print("="*60)

if __name__ == "__main__":
    main()