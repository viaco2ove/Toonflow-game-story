"""单角色转换测试"""
import sys, time, os, base64
sys.path.insert(0, ".")
from src.config import load_global_config
from src.toonflow.client import ToonflowClient

cfg = load_global_config()
cli = ToonflowClient(cfg)

role = sys.argv[1] if len(sys.argv) > 1 else "百晓生"
story_dir = "ai_story/android_sj/黑塔：从超忆症开始成神"
cache_dir = f".cache/character/黑塔：从超忆症开始成神/{role}"

# 找 mp4
mp4_files = sorted([f for f in os.listdir(cache_dir) if f.endswith(".mp4")], reverse=True)
if not mp4_files:
    print(f"[{role}] 缓存目录无 mp4")
    sys.exit(1)
mp4_path = os.path.join(cache_dir, mp4_files[0])
print(f"[{role}] 使用: {mp4_files[0]}")

with open(mp4_path, "rb") as f:
    mp4_data = f.read()
mp4_base64 = base64.b64encode(mp4_data).decode()

print(f"[{role}] 提交转换任务...")
r = cli.client.post("/game/convertAvatarVideoToGif", json={
    "fileData": mp4_base64,
    "fileName": f"{role}.mp4"
})
resp = r.json()
print(f"[{role}] 提交结果: {resp}")
task_id = resp.get("data", {}).get("taskId")
if not task_id:
    print(f"[{role}] 提交失败")
    sys.exit(1)

print(f"[{role}] taskId={task_id}，轮询中...")
for i in range(60):
    time.sleep(10)
    r2 = cli.client.post("/game/convertAvatarVideoToGif/status", json={"taskId": task_id})
    st = r2.json()
    data = st.get("data", {})
    status = data.get("status", "unknown")
    progress = data.get("progress", 0)
    print(f"[{role}] {i*10}s - status={status}, progress={progress}")
    if status in ("completed", "success"):
        print(f"[{role}] 完成！")
        sys.exit(0)
    if status in ("failed", "error"):
        print(f"[{role}] 失败: {data}")
        sys.exit(1)
print(f"[{role}] 超时")
sys.exit(1)
