import urllib.request, json, os, base64, time
from pathlib import Path

# 配置
BASE_URL = "http://122.51.232.171:60002"
TOKEN = "xxx"
PROJECT_ID = 1
WORLD_ID = 35
CHAPTER_ID = 52  # 第一章

# 图片目录
IMAGE_DIR = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/我的诡异表妹/image/我的诡异表妹"
BACKGROUND_FILE = "chapter_1_background.jpg"

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

def upload_image(file_path, image_type="scene"):
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
    
    # 调用上传API（使用scene类型）
    upload_data = {
        "projectId": PROJECT_ID,
        "type": "scene",
        "fileName": f"{image_type}_background.{ext}",
        "base64Data": base64_data
    }
    
    result = api_call("/game/uploadImage", upload_data)
    
    if result.get("code") == 200:
        return result.get("data", {}).get("filePath"), result.get("data", {}).get("path")
    else:
        print(f"上传失败: {result.get('message', '未知错误')}")
        return None, None

def update_chapter_background(background_path):
    """更新章节背景图设置"""
    # 获取当前世界设置
    result = api_call("/game/getWorld", {"worldId": WORLD_ID})
    if result.get("code") != 200:
        print(f"获取世界设置失败: {result.get('message')}")
        return False
    
    world_data = result.get("data", {})
    settings = world_data.get("settings", "{}")
    
    # 解析settings
    if isinstance(settings, str):
        try:
            settings = json.loads(settings)
        except:
            settings = {}
    
    # 更新chapterExtras中的background
    chapter_extras = settings.get("chapterExtras", [])
    for extra in chapter_extras:
        if extra.get("chapterId") == CHAPTER_ID:
            extra["background"] = background_path
            print(f"✓ 更新章节 {CHAPTER_ID} 背景图: {background_path}")
            break
    
    settings["chapterExtras"] = chapter_extras
    world_data["settings"] = settings
    
    # 保存更新（需要包含所有必填字段）
    update_data = {
        "worldId": WORLD_ID,
        "projectId": PROJECT_ID,
        "name": world_data.get("name", "我的诡异表妹"),
        "intro": world_data.get("intro", ""),
        "coverPath": world_data.get("coverPath", ""),
        "publishStatus": world_data.get("publishStatus", "draft"),
        "settings": settings,
        "playerRole": world_data.get("playerRole", {}),
        "narratorRole": world_data.get("narratorRole", {})
    }
    
    result = api_call("/game/saveWorld", update_data)
    if result.get("code") == 200:
        print("✓ 世界设置更新成功")
        return True
    else:
        print(f"✗ 世界设置更新失败: {result.get('message')}")
        return False

def main():
    print("=== 章节背景图上传工具 ===")
    print(f"服务器地址: {BASE_URL}")
    print(f"项目ID: {PROJECT_ID}")
    print(f"世界ID: {WORLD_ID}")
    print(f"章节ID: {CHAPTER_ID}")
    print(f"图片目录: {IMAGE_DIR}")
    print()
    
    # 检查图片目录是否存在
    if not os.path.exists(IMAGE_DIR):
        print(f"错误: 图片目录不存在: {IMAGE_DIR}")
        return
    
    # 上传背景图
    print("=== 上传章节背景图 ===")
    background_file = os.path.join(IMAGE_DIR, BACKGROUND_FILE)
    if not os.path.exists(background_file):
        print(f"错误: 背景图文件不存在: {background_file}")
        return
    
    background_path, background_web = upload_image(background_file, "chapter")
    if background_path:
        print(f"✓ 背景图上传成功: {background_path}")
        if background_web:
            print(f"  访问路径: {background_web}")
    else:
        print("✗ 背景图上传失败")
        return
    
    # 更新世界设置
    print("\n=== 更新世界设置 ===")
    if update_chapter_background(background_path):
        print("\n=== 上传完成 ===")
        print(f"章节背景图: {background_path}")
    else:
        print("\n=== 上传失败 ===")

if __name__ == "__main__":
    main()