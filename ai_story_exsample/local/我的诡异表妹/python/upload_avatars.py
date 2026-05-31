import urllib.request, json, os, base64, time
from pathlib import Path

# 配置
BASE_URL = "http://122.51.232.171:60002"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzc5OTEwMDA5LCJleHAiOjE3OTU0NjIwMDl9.FlDWRs9KmFo97rt9sob8emsQC5IXdVUZTlvC6wXCNL8"
PROJECT_ID = 1  # 我的诡异表妹项目ID
WORLD_ID = 35
AVATARS_DIR = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/我的诡异表妹/avatars"

# 角色文件名到角色ID的映射
ROLE_FILE_MAPPING = {
    "xiaoqi.png": "npc_xiaoqi",
    "sulaoshi.png": "npc_sulaoshi",
    "xiaozhang.png": "npc_xiaozhang",
    "liekounv.png": "npc_liekounv",
    "wumianren.png": "npc_wumianren",
    "changfanv.png": "npc_changfav",  # 长发女1
    "liming.png": "npc_liming",
    "wangsiyuan.png": "npc_wangsiyuan",
    "zhaoxiaopang.png": "npc_zhaoxiaopang",
    "lurenjia.png": "npc_lurenjia",
    "xufei.png": "player",
}

# 额外的角色映射（用于为多个角色使用同一个头像文件）
ADDITIONAL_ROLE_MAPPING = {
    "npc_changfany": "changfanv.png",  # 长发女2使用同一个头像文件
}

def api_call(path, data, is_binary=False, binary_data=None, content_type="application/json"):
    """调用API"""
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    }
    
    if is_binary:
        headers["Content-Type"] = content_type
        req_data = binary_data
    else:
        headers["Content-Type"] = "application/json"
        req_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=req_data,
        headers=headers,
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
    print("=== 角色头像上传工具 ===")
    print(f"服务器地址: {BASE_URL}")
    print(f"项目ID: {PROJECT_ID}")
    print(f"头像目录: {AVATARS_DIR}")
    print(f"角色数量: {len(ROLE_FILE_MAPPING) + len(ADDITIONAL_ROLE_MAPPING)}")
    print()
    
    # 检查头像目录是否存在
    if not os.path.exists(AVATARS_DIR):
        print(f"错误: 头像目录不存在: {AVATARS_DIR}")
        return
    
    # 获取所有头像文件
    avatar_files = [f for f in os.listdir(AVATARS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"找到 {len(avatar_files)} 个头像文件:")
    for file in avatar_files:
        print(f"  - {file}")
    print()
    
    # 上传每个头像
    results = []
    success_count = 0
    
    # 上传主要映射中的角色
    for filename, role_id in ROLE_FILE_MAPPING.items():
        file_path = os.path.join(AVATARS_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"[跳过] 文件不存在: {filename}")
            results.append({"role": role_id, "file": filename, "success": False, "error": "文件不存在"})
            continue
        
        print(f"[上传] {filename} -> {role_id}")
        
        # 上传图片
        file_path_server, web_path = upload_image(file_path, role_id)
        
        if file_path_server:
            print(f"  ✓ 上传成功: {file_path_server}")
            if web_path:
                print(f"  ✓ 访问路径: {web_path}")
            results.append({
                "role": role_id,
                "file": filename,
                "success": True,
                "server_path": file_path_server,
                "web_path": web_path
            })
            success_count += 1
        else:
            print(f"  ✗ 上传失败")
            results.append({"role": role_id, "file": filename, "success": False, "error": "上传失败"})
        
        # 添加延迟，避免请求过快
        time.sleep(0.5)
    
    # 上传额外映射中的角色（使用相同的头像文件）
    for role_id, filename in ADDITIONAL_ROLE_MAPPING.items():
        file_path = os.path.join(AVATARS_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"[跳过] 文件不存在: {filename}")
            results.append({"role": role_id, "file": filename, "success": False, "error": "文件不存在"})
            continue
        
        print(f"[上传] {filename} -> {role_id} (额外角色)")
        
        # 上传图片
        file_path_server, web_path = upload_image(file_path, role_id)
        
        if file_path_server:
            print(f"  ✓ 上传成功: {file_path_server}")
            if web_path:
                print(f"  ✓ 访问路径: {web_path}")
            results.append({
                "role": role_id,
                "file": filename,
                "success": True,
                "server_path": file_path_server,
                "web_path": web_path
            })
            success_count += 1
        else:
            print(f"  ✗ 上传失败")
            results.append({"role": role_id, "file": filename, "success": False, "error": "上传失败"})
        
        # 添加延迟，避免请求过快
        time.sleep(0.5)
    
    # 汇总结果
    print("\n" + "="*50)
    print("上传汇总")
    print("="*50)
    print(f"成功: {success_count}/{len(results)}")
    print()
    
    # 打印成功上传的角色
    if success_count > 0:
        print("成功上传的角色:")
        for r in results:
            if r["success"]:
                print(f"  ✓ {r['role']}: {r['server_path']}")
        print()
    
    # 打印失败的角色
    failed = [r for r in results if not r["success"]]
    if failed:
        print("失败的角色:")
        for r in failed:
            print(f"  ✗ {r['role']}: {r.get('error', '未知错误')}")
        print()
    
    # 保存结果到JSON
    result_json_path = os.path.join(AVATARS_DIR, "upload_results.json")
    with open(result_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到: {result_json_path}")
    
    # 提示下一步操作
    if success_count > 0:
        print("\n=== 下一步操作 ===")
        print("1. 将上传的头像路径更新到世界设置中")
        print("2. 使用以下代码更新世界设置:")
        print("""
# 示例代码：更新世界设置中的角色头像路径
update_data = {
    "worldId": 35,
    "projectId": 1,
    "settings": {
        "roles": [
            {
                "id": "npc_xiaoqi",
                "name": "小七",
                "avatarPath": "/1/game/role/xxx.png",
                # ... 其他角色属性
            },
            # ... 其他角色
        ]
    }
}
result = api_call("/game/saveWorld", update_data)
""")

if __name__ == "__main__":
    main()