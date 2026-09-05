"""
批量本地 MODNet 转换 mp4 → webp + background.png
先生已转换跳过，其余 12 个角色并行跑
"""
import os, sys, subprocess, glob, time, json, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = r"D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story"
CACHE = os.path.join(ROOT, ".cache", "character", "黑塔：从超忆症开始成神")
VENV_PY = r"D:\Users\viaco\tools\Toonflow-game\Toonflow-game-app\Toonflow-game\tools\avatar-matting\birefnet\venv\Scripts\python.exe"
CONVERT = os.path.join(ROOT, ".workbuddy", "skills", "convert-avatar-video-to-webp", "convert.py")

# (subdir, mp4_filename)
ROLE_MAP = [
    ("用户", "陈曦_6s.mp4"),
    ("张晚意", "张晚意.mp4"),
    ("林凡", "林凡_6s.mp4"),
    ("老周", "老周.mp4"),
    ("苏晓", "苏晓.mp4"),
    ("魏叔", "魏叔_6s.mp4"),
    ("陈母", "陈母.mp4"),
    ("百晓生", "百晓生_6s.mp4"),
    ("白子轩", "白子轩_6s.mp4"),
    ("小满", "小满_6s.mp4"),
    ("某女子", "某女子_6s.mp4"),
    ("某男子", "某男子_6s.mp4"),
]

def get_role_name(subdir, mp4file):
    """从 subdir/mp4file 反推角色显示名"""
    # 直接从目录名取
    return subdir

def check_done(subdir):
    out_dir = os.path.join(CACHE, subdir, "webp")
    fg = os.path.join(out_dir, "foreground.webp")
    bg = os.path.join(out_dir, "background.png")
    return os.path.exists(fg) and os.path.exists(bg)

def convert_one(subdir, mp4file):
    mp4_path = os.path.join(CACHE, subdir, mp4file)
    out_dir = os.path.join(CACHE, subdir, "webp")
    os.makedirs(out_dir, exist_ok=True)

    # skip if already done
    if check_done(subdir):
        return subdir, "already_done", None

    if not os.path.exists(mp4_path):
        return subdir, "skip_no_mp4", None

    print(f"[START] {subdir}: {mp4file}")
    err_log = os.path.join(out_dir, "_convert_err.log")
    out_log = os.path.join(out_dir, "_convert_out.log")

    cmd = [VENV_PY, CONVERT, "--mp4", mp4_path, "--out-dir", out_dir, "--keep-tmp"]
    try:
        with open(err_log, "w", encoding="utf-8") as fe:
            with open(out_log, "w", encoding="utf-8") as fo:
                rc = subprocess.call(cmd, stdout=fo, stderr=fe)
        if rc == 0 and check_done(subdir):
            return subdir, "ok", None
        else:
            err_content = open(err_log, encoding="utf-8", errors="replace").read()
            return subdir, f"fail_rc={rc}", err_content[:300]
    except Exception as e:
        return subdir, f"error: {e}", None

def main():
    results = []
    total = len(ROLE_MAP)

    # 并发跑（MODNet CPU 推理，约 1 个/分钟）
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(convert_one, subdir, mp4): (subdir, mp4) for subdir, mp4 in ROLE_MAP}
        done = 0
        for future in as_completed(futures):
            done += 1
            subdir, mp4 = futures[future]
            try:
                role, status, err = future.result()
            except Exception as e:
                role, status, err = subdir, f"exception: {e}", None
            results.append((role, status, err))
            print(f"[PROGRESS] {done}/{total} done: {role} -> {status}")

    # 汇总
    ok = [r for r in results if "ok" in r[1] or "already" in r[1]]
    fail = [r for r in results if r not in ok]
    print(f"\n=== RESULT: {len(ok)} OK, {len(fail)} FAILED ===")
    for role, status, err in fail:
        print(f"  FAIL: {role} -> {status} | {err or ''}")

    # 写结果 JSON
    result_file = os.path.join(ROOT, ".cache", "batch_convert_result.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({"ok": [r[0] for r in ok], "fail": [(r[0], r[1]) for r in fail]}, f, ensure_ascii=False, indent=2)
    print(f"Result written to {result_file}")

if __name__ == "__main__":
    main()
