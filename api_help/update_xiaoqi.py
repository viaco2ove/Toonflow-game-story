import urllib.request, json, os, base64, time
from pathlib import Path

# 配置
BASE_URL = "http://122.51.232.171:60002"
TOKEN = "***REMOVED***"
PROJECT_ID = 1
WORLD_ID = 35
AVATARS_DIR = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/我的诡异表妹/avatars"

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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": 500, "message": str(e)}

def upload_image(file_path, role_id):
    """上传图片到服务器"""
    # 读取图片文件并转换为base64
    with open(file_path, "rb") as f:
        image_data = f.read()
    
    # 获取文件扩展名
    ext = Path(file_path).suffix.lower().strip(".")
    if ext == "jpeg":
        ext = "jpg"
    
    # 构建base64字符串
    mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    base64_data = f"data:{mime_type};base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    # 调用上传API
    upload_data = {
        "projectId": PROJECT_ID,
        "type": "role",
        "fileName": f"{role_id}.{ext}",
        "base64Data": base64_data
    }
    
    result = api_call("/game/uploadImage", upload_data)
    
    if result.get("code") == 200:
        return result.get("data", {}).get("filePath"), result.get("data", {}).get("path")
    else:
        print(f"上传失败: {result.get('message', '未知错误')}")
        return None, None

def main():
    print("=== 更新小七角色信息和头像 ===")
    print(f"服务器地址: {BASE_URL}")
    print(f"世界ID: {WORLD_ID}")
    print(f"项目ID: {PROJECT_ID}")
    print()
    
    # 1. 上传新的头像
    print("=== 1. 上传新的头像 ===")
    new_avatar_path = os.path.join(AVATARS_DIR, "xiaoqi_new.jpg")
    if not os.path.exists(new_avatar_path):
        print(f"错误: 新头像文件不存在: {new_avatar_path}")
        return
    
    print(f"上传新头像: {new_avatar_path}")
    file_path_server, web_path = upload_image(new_avatar_path, "npc_xiaoqi")
    
    if not file_path_server:
        print("头像上传失败")
        return
    
    print(f"✓ 头像上传成功: {file_path_server}")
    if web_path:
        print(f"✓ 访问路径: {web_path}")
    
    # 2. 获取当前世界数据
    print("\n=== 2. 获取当前世界数据 ===")
    world_resp = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if world_resp.get("code") != 200:
        print(f"获取世界失败: {world_resp}")
        return
    
    world_data = world_resp.get("data", {})
    settings_str = world_data.get("settings", "{}")
    settings = json.loads(settings_str) if isinstance(settings_str, str) else settings_str
    
    # 3. 更新小七的角色信息
    print("\n=== 3. 更新小七的角色信息 ===")
    existing_roles = settings.get("roles", [])
    xiaoqi_updated = False
    
    for role in existing_roles:
        if role.get("id") == "npc_xiaoqi":
            # 更新头像路径
            role["avatarPath"] = file_path_server
            role["avatarUrl"] = web_path or ""
            
            # 更新角色描述
            role["description"] = "用户去找表妹时因为眼镜坏了，认错了你,你讲错就错成了用户的便宜表妹， 外表与人类少女相似，皮肤惨败：乌黑及腰的长发，齐刘海下藏着一双弯月眼，笑起来却无情冷酷，声音冷酷无情。但仔细看——她的瞳孔在光线昏暗处会瞬间收缩成冰冷的竖瞳，灯光下的影子永远会无声分裂成两道，边缘泛着常人看不见的黑雾。\n你称呼用户为表哥（用户）。在诡异世界保护用户。\n\n她永远穿着一身纯黑色的修身校服，没有任何校徽和标识，布料是一种不反光的哑光材质，仿佛能吞噬周围的光线。领口别着那枚古怪的黑色发卡，是她身上唯一的装饰，也是压制她滔天诡异气息的唯一道具。在满是白色校服的校园里，她的黑色身影格外扎眼，却没有任何学生或诡异敢多看她一眼——所有试图挑衅她的存在，都已经彻底消失在了影子里。"
            
            # 更新角色参数
            role["rawSetting"] = "诡异世界中的高级诡异（冥尊 5 星，77级），外表与用户的表妹完全一致。出于未知原因，选择保护用户这个误入的异类。实力强大，在学校的诡异中位居上位，仅次于校长和苏老师。她刻意选择纯黑色校服作为自己的标识，既是对自身诡异身份的坦然，也是对所有潜在威胁的无声警告。"
            role["gender"] = "女"
            role["age"] = 19
            role["level"] = 77
            role["levelDesc"] = "冥尊 5 星"
            role["personality"] = "表面温和乖巧；实则冷酷残忍到极致，对任何可能威胁到用户的存在，无论人畜还是诡异，都会毫不犹豫地抹杀，没有任何怜悯和犹豫"
            role["appearance"] = "乌黑及腰长发，齐刘海，浅浅的酒窝，皮肤在黑色校服的衬托下显得异常苍白。永远穿着一身纯黑色哑光修身校服，无校徽无标识，黑色过膝袜，黑色圆头皮鞋。领口别着一枚黑色诡异发卡。平时是人类圆瞳，情绪波动或释放力量时会变成冰冷的金色竖瞳，影子永远分裂为两道"
            role["skills"] = ["诡异守护", "影子吞噬", "气息压制"]
            role["equipment"] = ["黑色发卡（冥尊级诡异道具，可完全压制自身气息，同时能吸收周围的诡异能量）"]
            role["hp"] = 1000
            role["mp"] = 500
            role["other"] = ["真实身份：学校三大上位诡异之一", "与用户表妹的关系：未知", "黑色校服：由她自身的诡异能量凝聚而成，刀枪不入，能免疫所有低级诡异的攻击"]
            
            xiaoqi_updated = True
            print(f"✓ 已更新小七角色信息")
            print(f"  头像路径: {file_path_server}")
            print(f"  角色描述: 已更新")
            print(f"  角色参数: 已更新")
            break
    
    if not xiaoqi_updated:
        print("✗ 未找到小七角色")
        return
    
    # 4. 保存更新后的世界
    print("\n=== 4. 保存更新后的世界 ===")
    settings["roles"] = existing_roles
    
    save_data = {
        "worldId": WORLD_ID,
        "projectId": world_data.get("projectId", PROJECT_ID),
        "name": world_data.get("name", "我的诡异表妹"),
        "intro": world_data.get("intro", ""),
        "settings": settings,
    }
    
    # 保留玩家角色和旁白角色
    if world_data.get("playerRole"):
        save_data["playerRole"] = world_data["playerRole"]
    if world_data.get("narratorRole"):
        save_data["narratorRole"] = world_data["narratorRole"]
    
    save_resp = api_call("/game/saveWorld", save_data)
    print(f"保存结果: {save_resp.get('code')} - {save_resp.get('message', '无消息')}")
    
    if save_resp.get("code") == 200:
        print(f"\n=== 完成 ===")
        print(f"小七角色信息和头像已成功更新")
    else:
        print(f"\n保存失败详情: {json.dumps(save_resp, ensure_ascii=False, indent=2)}")
    
    # 5. 验证更新
    print("\n=== 5. 验证更新 ===")
    verify_resp = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if verify_resp.get("code") == 200:
        verify_data = verify_resp.get("data", {})
        verify_settings_str = verify_data.get("settings", "{}")
        verify_settings = json.loads(verify_settings_str) if isinstance(verify_settings_str, str) else verify_settings_str
        
        verify_roles = verify_settings.get("roles", [])
        for role in verify_roles:
            if role.get("id") == "npc_xiaoqi":
                print(f"✓ 小七角色验证:")
                print(f"  头像路径: {role.get('avatarPath', '无')}")
                print(f"  角色描述: {role.get('description', '无')[:50]}...")
                break

if __name__ == "__main__":
    main()