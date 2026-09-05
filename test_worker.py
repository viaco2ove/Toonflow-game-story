"""单角色 webp 转换测试（使用现有 webp_avatar_sync 逻辑）"""
import sys, os, time
sys.path.insert(0, ".")
from src.config import load_global_config
from src.toonflow.webp_avatar_sync import convert_video_to_webp

cfg = load_global_config()
role = sys.argv[1] if len(sys.argv) > 1 else "百晓生"
cache_dir = f".cache/character/黑塔：从超忆症开始成神/{role}"

mp4_files = sorted([f for f in os.listdir(cache_dir) if f.endswith(".mp4")], reverse=True)
print(f"[{role}] 可用 mp4: {mp4_files}")
mp4_path = os.path.join(cache_dir, mp4_files[0])
print(f"[{role}] 使用: {mp4_path}")

from src.toonflow.client import ToonflowClient
cli = ToonflowClient(cfg)

print(f"[{role}] 开始转换...")
try:
    result = convert_video_to_webp(cli, mp4_path, project_id=1)
    print(f"[{role}] ✅ 成功！")
    print(f"  foreground: {result.get('foregroundFilePath')}")
    print(f"  background: {result.get('backgroundFilePath')}")
    print(f"  video:      {result.get('videoPath')}")
except Exception as e:
    print(f"[{role}] ❌ 失败: {e}")
