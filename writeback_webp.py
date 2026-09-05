"""
把本地 .cache 里的 webp 批量写回 world 44
先生和陈曦已有 webp 先写，其余 10 个并行转 base64 写回
"""
import os, sys, base64, glob, time, json, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '.')
from src.config import load_global_config
from src.toonflow.client import ToonflowClient

def img_to_b64(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return b64

ROOT = r"D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story"
CACHE = os.path.join(ROOT, ".cache", "character", "黑塔：从超忆症开始成神")

# subdir → 角色名映射（去 world 44 里找）
SUBDIR_TO_ROLE = {
    "先生": "先生",
    "用户": "陈曦",
    "张晚意": "张晚意",
    "林凡": "林凡",
    "老周": "老周",
    "苏晓": "苏晓",
    "魏叔": "魏叔",
    "陈母": "陈母",
    "百晓生": "百晓生",
    "白子轩": "白子轩",
    "小满": "小满",
    "某女子": "某女子",
    "某男子": "某男子",
}

def get_webp_files(subdir):
    webp_dir = os.path.join(CACHE, subdir, "webp")
    fg = os.path.join(webp_dir, "foreground.webp")
    bg = os.path.join(webp_dir, "background.png")
    ff = os.path.join(webp_dir, "firstFrame.png")
    return fg, bg, ff

def load_world_44(cfg):
    cli = ToonflowClient(cfg)
    w = cli.get_world(44)
    w["worldId"] = 44  # 关键：补 worldId
    return cli, w

def find_role(w, name):
    if w.get("playerRole", {}).get("name") == name:
        return w["playerRole"]
    for r in w.get("settings", {}).get("roles", []):
        if r.get("name") == name:
            return r
    return None

def write_back_one(subdir, cli, world, results):
    role_name = SUBDIR_TO_ROLE.get(subdir, subdir)
    fg, bg, ff = get_webp_files(subdir)

    # base64
    fg_b64 = img_to_b64(fg)
    bg_b64 = img_to_b64(bg)
    ff_b64 = img_to_b64(ff)

    role = find_role(world, role_name)
    if not role:
        results.append((subdir, "role_not_found"))
        return

    role["avatarUrl"] = fg_b64
    role["avatarMiddleUrl"] = bg_b64
    role["avatarBackgroundUrl"] = ff_b64
    role["avatarThumbUrl"] = fg_b64

    print(f"[OK] {subdir} ({role_name}) -> world 44")
    results.append((subdir, "ok"))

def main():
    print("Loading world 44...")
    cfg = load_global_config()
    cli, world = load_world_44(cfg)

    # 先找出哪些 subdir 有 webp
    ready = []
    for subdir in SUBDIR_TO_ROLE:
        fg, bg, ff = get_webp_files(subdir)
        if os.path.exists(fg) and os.path.exists(bg):
            ready.append(subdir)
        else:
            print(f"[SKIP] {subdir}: webp not ready")

    print(f"\nSyncing {len(ready)} roles to world 44...")

    results = []
    threads = []
    for subdir in ready:
        t = threading.Thread(target=write_back_one, args=(subdir, cli, world, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # 保存
    print("\nSaving world 44...")
    cli.save_world(world)
    print("DONE")

    ok = [r for r in results if r[1] == "ok"]
    fail = [r for r in results if r[1] != "ok"]
    print(f"\n=== {len(ok)} OK, {len(fail)} FAILED ===")
    for r, s in fail:
        print(f"  FAIL: {r} -> {s}")

if __name__ == "__main__":
    main()