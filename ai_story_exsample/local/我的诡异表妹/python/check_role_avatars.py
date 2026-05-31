import urllib.request, json

# 配置
BASE_URL = "http://122.51.232.171:60002"
TOKEN = "***REMOVED***"
WORLD_ID = 35

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
    print("=== 检查角色头像状态 ===")
    print(f"服务器地址: {BASE_URL}")
    print(f"世界ID: {WORLD_ID}")
    print()
    
    # 获取世界数据
    world_resp = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if world_resp.get("code") != 200:
        print(f"获取世界失败: {world_resp}")
        return
    
    world_data = world_resp.get("data", {})
    settings_str = world_data.get("settings", "{}")
    settings = json.loads(settings_str) if isinstance(settings_str, str) else settings_str
    
    # 获取所有角色
    roles = settings.get("roles", [])
    print(f"角色总数: {len(roles)}")
    print()
    
    # 检查每个角色的头像状态
    avatar_status = {
        "has_avatar": [],
        "no_avatar": [],
        "has_url": []
    }
    
    for role in roles:
        role_id = role.get("id", "")
        role_name = role.get("name", "")
        avatar_path = role.get("avatarPath", "")
        avatar_url = role.get("avatarUrl", "")
        
        if avatar_path:
            avatar_status["has_avatar"].append({
                "id": role_id,
                "name": role_name,
                "path": avatar_path,
                "url": avatar_url
            })
        else:
            avatar_status["no_avatar"].append({
                "id": role_id,
                "name": role_name
            })
        
        if avatar_url:
            avatar_status["has_url"].append({
                "id": role_id,
                "name": role_name,
                "url": avatar_url
            })
    
    # 打印结果
    print("=== 有头像的角色 ===")
    for item in avatar_status["has_avatar"]:
        print(f"  ✓ {item['name']} ({item['id']})")
        print(f"    路径: {item['path']}")
        if item['url']:
            print(f"    URL: {item['url']}")
        print()
    
    print("=== 无头像的角色 ===")
    for item in avatar_status["no_avatar"]:
        print(f"  ✗ {item['name']} ({item['id']})")
    
    print()
    print("=== 有头像URL的角色 ===")
    for item in avatar_status["has_url"]:
        print(f"  ✓ {item['name']}: {item['url']}")
    
    # 统计
    print()
    print("=== 统计 ===")
    print(f"有头像的角色: {len(avatar_status['has_avatar'])}")
    print(f"无头像的角色: {len(avatar_status['no_avatar'])}")
    print(f"有头像URL的角色: {len(avatar_status['has_url'])}")
    
    # 检查玩家角色
    player_role = world_data.get("playerRole")
    if player_role:
        if isinstance(player_role, str):
            player_role = json.loads(player_role)
        
        print()
        print("=== 玩家角色 ===")
        print(f"名称: {player_role.get('name', '')}")
        print(f"头像路径: {player_role.get('avatarPath', '无')}")
        print(f"头像URL: {player_role.get('avatarUrl', '无')}")
    
    # 检查旁白角色
    narrator_role = world_data.get("narratorRole")
    if narrator_role:
        if isinstance(narrator_role, str):
            narrator_role = json.loads(narrator_role)
        
        print()
        print("=== 旁白角色 ===")
        print(f"名称: {narrator_role.get('name', '')}")
        print(f"头像路径: {narrator_role.get('avatarPath', '无')}")
        print(f"头像URL: {narrator_role.get('avatarUrl', '无')}")

if __name__ == "__main__":
    main()