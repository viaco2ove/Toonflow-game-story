# debug_batch.py - 直接跑，不走 argparse stdout 管道
import sys, os, traceback, base64, time, json
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)  # 行缓冲

from src.config import load_global_config
from src.toonflow.client import ToonflowClient

STORY = "黑塔：从超忆症开始成神"
CACHE = os.path.join(os.path.dirname(__file__), ".cache", "character", STORY)
WORLD_ID = 44

ROLE_MP4 = {
    "陈曦":  ("用户",   "陈曦_6s.mp4"),
    "张晚意": ("张晚意", "张晚意.mp4"),
    "林凡":  ("林凡",   "林凡_6s.mp4"),
    "老周":  ("老周",   "老周.mp4"),
    "苏晓":  ("苏晓",   "苏晓.mp4"),
    "魏叔":  ("魏叔",   "魏叔_6s.mp4"),
    "陈母":  ("陈母",   "陈母.mp4"),
    "百晓生": ("百晓生", "百晓生_6s.mp4"),
    "白子轩": ("白子轩", "白子轩_6s.mp4"),
    "小满":  ("小满",   "小满_6s.mp4"),
    "某女子": ("某女子", "某女子_6s.mp4"),
    "某男子": ("某男子", "某男子_6s.mp4"),
}

def log(msg):
    print(msg, flush=True)

def submit(client, role):
    subdir, mp4name = ROLE_MP4[role]
    mp4 = os.path.join(CACHE, subdir, mp4name)
    if not os.path.exists(mp4):
        return role, None, f"找不到 mp4: {mp4}"
    log(f"[{role}] 读取 {mp4}")
    b64 = base64.b64encode(open(mp4, "rb").read()).decode("ascii")
    payload = {
        "projectId": 1,
        "fileName": f"{role}.mp4",
        "base64Data": f"data:video/mp4;base64,{b64}",
    }
    r = client.api_call("/game/convertAvatarVideoToGif", payload, timeout=180)
    if r.get("code") != 200:
        return role, None, f"提交失败: {r}"
    task_id = r["data"]["taskId"]
    log(f"[{role}] taskId={task_id} 提交成功")
    return role, task_id, None

def poll(client, role, task_id):
    waited = 0
    while waited < 900:
        st = client.api_call("/game/convertAvatarVideoToGif/status",
                             {"taskId": task_id}, timeout=30)
        d = st.get("data", {})
        status = d.get("status")
        log(f"[{role}] status={status} progress={d.get('progress')}% {d.get('message','')}")
        if status == "success":
            return role, d, None
        if status == "failed":
            return role, None, d.get("errorMessage") or "failed"
        time.sleep(5)
        waited += 5
    return role, None, f"超时"

def writeback(client, results, world_id=WORLD_ID):
    world = client.get_world(world_id)
    settings = world.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)
    updated = []
    for r in settings.get("roles", []):
        if r.get("name") in results:
            d = results[r["name"]]
            r["avatarPath"] = d.get("foregroundFilePath")
            r["avatarBgPath"] = d.get("backgroundFilePath")
            r["avatarVideoPath"] = d.get("videoPath")
            r["avatarFirstFramePath"] = d.get("firstFramePath")
            r["avatarDurationMs"] = d.get("durationMs")
            updated.append(r["name"])
    pr = world.get("playerRole", {})
    if pr.get("name") in results:
        d = results[pr["name"]]
        pr["avatarPath"] = d.get("foregroundFilePath")
        pr["avatarBgPath"] = d.get("backgroundFilePath")
        pr["avatarVideoPath"] = d.get("videoPath")
        pr["avatarFirstFramePath"] = d.get("firstFramePath")
        pr["avatarDurationMs"] = d.get("durationMs")
        updated.append(pr["name"])
    world["settings"] = settings
    world["id"] = world_id
    world["worldId"] = world_id
    client.save_world(world)
    log(f"写回完成: {updated}")

def main():
    cfg = load_global_config()
    client = ToonflowClient(cfg)
    log(f"Connected to {cfg.base_url}")

    roles = sys.argv[1:] if len(sys.argv) > 1 else list(ROLE_MP4.keys())
    log(f"处理角色: {roles}")

    # Phase 1: 提交
    tasks = []
    for role in roles:
        if role not in ROLE_MP4:
            log(f"跳过未知角色: {role}")
            continue
        r, tid, err = submit(client, role)
        if err:
            log(f"[{role}] 提交失败: {err}")
        else:
            tasks.append((role, tid))

    # Phase 2: 轮询
    results = {}
    for role, tid in tasks:
        r, d, err = poll(client, role, tid)
        if err:
            log(f"[{role}] 失败: {err}")
        else:
            log(f"[{role}] 成功!")
            results[role] = d

    if results:
        writeback(client, results)

    log(f"=== 完成: {len(results)}/{len(roles)} ===")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()