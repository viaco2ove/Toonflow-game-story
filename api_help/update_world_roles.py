import urllib.request, json, os

# 配置
BASE_URL = "http://122.51.232.171:60002"
TOKEN = "***REMOVED***"
WORLD_ID = 35
PROJECT_ID = 1

# 上传结果文件路径
UPLOAD_RESULTS_PATH = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/我的诡异表妹/avatars/upload_results.json"

def api_call(path, data):
    """调用API"""
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
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": 500, "message": str(e)}

def main():
    print("=== 更新世界设置中的角色头像路径 ===")
    print(f"服务器地址: {BASE_URL}")
    print(f"世界ID: {WORLD_ID}")
    print(f"项目ID: {PROJECT_ID}")
    print()
    
    # 1. 加载上传结果
    if not os.path.exists(UPLOAD_RESULTS_PATH):
        print(f"错误: 上传结果文件不存在: {UPLOAD_RESULTS_PATH}")
        print("请先运行 upload_avatars.py 上传头像")
        return
    
    with open(UPLOAD_RESULTS_PATH, "r", encoding="utf-8") as f:
        upload_results = json.load(f)
    
    print(f"加载上传结果: {len(upload_results)} 个角色")
    
    # 2. 获取当前世界数据
    print("\n=== 1. 获取当前世界数据 ===")
    world_resp = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if world_resp.get("code") != 200:
        print(f"获取世界失败: {world_resp}")
        return
    
    world_data = world_resp.get("data", {})
    settings_str = world_data.get("settings", "{}")
    settings = json.loads(settings_str) if isinstance(settings_str, str) else settings_str
    
    # 获取现有角色列表
    existing_roles = settings.get("roles", [])
    print(f"现有角色数: {len(existing_roles)}")
    for r in existing_roles:
        print(f"  - {r.get('name', '?')} ({r.get('id', '?')})")
    
    # 3. 创建角色ID到上传结果的映射
    upload_map = {r["role"]: r for r in upload_results if r["success"]}
    print(f"\n成功上传的角色: {len(upload_map)}")
    
    # 4. 更新现有角色的头像路径
    updated_count = 0
    for role in existing_roles:
        role_id = role.get("id", "")
        if role_id in upload_map:
            upload_info = upload_map[role_id]
            old_avatar = role.get("avatarPath", "")
            role["avatarPath"] = upload_info["server_path"]
            role["avatarUrl"] = upload_info.get("web_path", "")
            updated_count += 1
            print(f"更新角色头像: {role.get('name', role_id)}")
            print(f"  旧路径: {old_avatar or '无'}")
            print(f"  新路径: {upload_info['server_path']}")
    
    # 5. 保存更新后的世界
    print("\n=== 2. 保存更新后的世界 ===")
    
    # 重新构建settings（保持其他字段不变）
    settings["roles"] = existing_roles
    
    save_data = {
        "worldId": WORLD_ID,
        "projectId": world_data.get("projectId", PROJECT_ID),
        "name": world_data.get("name", "我的诡异表妹"),
        "intro": world_data.get("intro", ""),
        "settings": settings,
    }
    
    # 如果有playerRole和narratorRole，保留它们
    if world_data.get("playerRole"):
        player_role = world_data["playerRole"]
        if isinstance(player_role, str):
            player_role = json.loads(player_role)
        
        # 更新玩家角色的头像路径
        if "player" in upload_map:
            player_role["avatarPath"] = upload_map["player"]["server_path"]
            player_role["avatarUrl"] = upload_map["player"].get("web_path", "")
            print("更新玩家角色头像")
        
        save_data["playerRole"] = player_role
    
    if world_data.get("narratorRole"):
        narrator_role = world_data["narratorRole"]
        if isinstance(narrator_role, str):
            narrator_role = json.loads(narrator_role)
        save_data["narratorRole"] = narrator_role
    
    save_resp = api_call("/game/saveWorld", save_data)
    print(f"保存结果: {save_resp.get('code')} - {save_resp.get('message', '无消息')}")
    
    if save_resp.get("code") == 200:
        print(f"\n=== 完成 ===")
        print(f"更新角色头像: {updated_count}")
        print(f"世界设置已保存")
    else:
        print(f"\n保存失败详情: {json.dumps(save_resp, ensure_ascii=False, indent=2)}")
    
    # 6. 验证更新
    print("\n=== 3. 验证更新 ===")
    verify_resp = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if verify_resp.get("code") == 200:
        verify_data = verify_resp.get("data", {})
        verify_settings_str = verify_data.get("settings", "{}")
        verify_settings = json.loads(verify_settings_str) if isinstance(verify_settings_str, str) else verify_settings_str
        
        verify_roles = verify_settings.get("roles", [])
        print(f"验证角色数: {len(verify_roles)}")
        
        for role in verify_roles:
            role_id = role.get("id", "")
            avatar_path = role.get("avatarPath", "")
            avatar_url = role.get("avatarUrl", "")
            
            if role_id in upload_map:
                expected_path = upload_map[role_id]["server_path"]
                if avatar_path == expected_path:
                    print(f"  ✓ {role.get('name', role_id)}: 头像路径已正确更新")
                else:
                    print(f"  ✗ {role.get('name', role_id)}: 头像路径不匹配")
                    print(f"    期望: {expected_path}")
                    print(f"    实际: {avatar_path}")
    
    # 7. 保存更新结果
    update_result = {
        "worldId": WORLD_ID,
        "updated_roles": updated_count,
        "roles": []
    }
    
    for role in existing_roles:
        role_id = role.get("id", "")
        if role_id in upload_map:
            update_result["roles"].append({
                "id": role_id,
                "name": role.get("name", ""),
                "avatarPath": role.get("avatarPath", ""),
                "avatarUrl": role.get("avatarUrl", "")
            })
    
    result_path = os.path.join(os.path.dirname(UPLOAD_RESULTS_PATH), "world_update_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(update_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n更新结果已保存到: {result_path}")

if __name__ == "__main__":
    main()