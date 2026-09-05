"""
batch_webp_sync.py - 批量把 .cache 里的角色 mp4 上传转换 webp+png，并一次性写回 world 44

流程:
  Phase 1: 逐个提交 /game/convertAvatarVideoToGif (mp4 base64)，收集 taskId
  Phase 2: 轮询所有 taskId 直到 success/failed
  Phase 3: get_world(44) 一次，批量更新角色字段，补 worldId 后 save_world 一次
  Phase 4: 下载 webp/png 到本地 .cache 留档

用法:
  python -m src.toonflow.batch_webp_sync --roles 张晚意 林凡 老周
  python -m src.toonflow.batch_webp_sync --roles 陈曦 --world-id 44
"""
import sys
import base64
import time
import json
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.config import load_global_config
from src.toonflow.client import ToonflowClient

STORY = "黑塔：从超忆症开始成神"
CACHE = ROOT / ".cache" / "character" / STORY
WORLD_ID = 44

# role_name -> (cache_dir_name, mp4_name)
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
    "先生":  ("先生",   "先生_2026-09-04T16-41-32.mp4"),
}


def submit(client: ToonflowClient, role: str, project_id: int = 1):
    """Phase 1: 提交单个转换任务"""
    subdir, mp4name = ROLE_MP4[role]
    mp4 = CACHE / subdir / mp4name
    if not mp4.exists():
        return role, None, f"找不到 mp4: {mp4}"
    b64 = base64.b64encode(mp4.read_bytes()).decode("ascii")
    payload = {
        "projectId": project_id,
        "fileName": f"{role}.mp4",  # 用角色名做文件名，服务端日志可读
        "base64Data": f"data:video/mp4;base64,{b64}",
    }
    r = client.api_call("/game/convertAvatarVideoToGif", payload, timeout=180)
    if r.get("code") != 200:
        return role, None, f"提交失败: {r.get('message')}"
    task_id = r["data"]["taskId"]
    print(f"  [{role}] 已提交 taskId={task_id}")
    return role, task_id, None


def poll(client: ToonflowClient, role: str, task_id: int,
         interval: int = 5, max_wait: int = 900):
    """Phase 2: 轮询单个任务直到结束"""
    waited = 0
    last = ""
    while waited < max_wait:
        st = client.api_call("/game/convertAvatarVideoToGif/status",
                             {"taskId": task_id}, timeout=30)
        d = st.get("data", {})
        msg = f"{d.get('status')} {d.get('progress')}%"
        if msg != last:
            print(f"  [{role}] {msg} {d.get('message', '')}")
            last = msg
        if d.get("status") == "success":
            return role, d, None
        if d.get("status") == "failed":
            return role, None, d.get("errorMessage") or "failed"
        time.sleep(interval)
        waited += interval
    return role, None, f"超时 {max_wait}s"


def writeback(client: ToonflowClient, results: dict, world_id: int = WORLD_ID):
    """Phase 3: 一次性写回所有角色（单次 save_world）"""
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
    world["worldId"] = world_id  # ⚠️ 必须，否则会新建世界
    client.save_world(world)
    print(f"  ✓ 一次 save_world 写回 {len(updated)} 个角色: {updated}")


def download_assets(client: ToonflowClient, results: dict):
    """Phase 4: webp/png 落地到本地缓存留档"""
    import requests as rq
    base = client.base_url
    headers = {"Authorization": f"Bearer {client.token}"}
    for role, d in results.items():
        subdir = ROLE_MP4[role][0]
        outdir = CACHE / subdir
        for key, fname in (("foregroundFilePath", "avatar.webp"),
                           ("backgroundFilePath", "background.png")):
            p = d.get(key)
            if not p:
                continue
            url = p if p.startswith("http") else base + p
            try:
                resp = rq.get(url, headers=headers, timeout=60)
                resp.raise_for_status()
                (outdir / fname).write_bytes(resp.content)
                print(f"  [{role}] 已下载 {fname} ({len(resp.content)/1024:.0f} KB)")
            except Exception as e:
                print(f"  [{role}] 下载 {fname} 失败: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roles", nargs="+", required=True)
    ap.add_argument("--world-id", type=int, default=WORLD_ID)
    ap.add_argument("--skip-convert", action="store_true",
                    help="跳过转换，直接用 --results-file 写回")
    ap.add_argument("--results-file", default=None)
    ap.add_argument("--no-writeback", action="store_true")
    ap.add_argument("--no-download", action="store_true")
    args = ap.parse_args()

    cfg = load_global_config()
    client = ToonflowClient(cfg)

    if args.skip_convert:
        results = {k: v for k, v in json.loads(
            Path(args.results_file).read_text(encoding="utf-8")).items()}
    else:
        # Phase 1: 顺序提交（大 payload 不宜并发打满带宽）
        tasks = []
        for role in args.roles:
            if role not in ROLE_MP4:
                print(f"  !! 未知角色 {role}，跳过")
                continue
            r = submit(client, role)
            if r[2]:
                print(f"  [{role}] ✗ {r[2]}")
            else:
                tasks.append((r[0], r[1]))
        print(f"\n=== 已提交 {len(tasks)} 个任务，开始轮询 ===\n")
        # Phase 2: 并发轮询
        results = {}
        with ThreadPoolExecutor(max_workers=min(6, len(tasks) or 1)) as ex:
            futs = [ex.submit(poll, client, role, tid) for role, tid in tasks]
            for f in futs:
                role, d, err = f.result()
                if err:
                    print(f"  [{role}] ✗ {err}")
                else:
                    print(f"  [{role}] ✓ 完成 webp={d.get('foregroundFilePath')}")
                    results[role] = d

        # 留档转换结果，便于断点重试写回
        if results:
            out = ROOT / ".cache" / f"webp_results_{int(time.time())}.json"
            out.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                           encoding="utf-8")
            print(f"\n  转换结果已留档: {out}")

    if results and not args.no_writeback:
        print("\n=== 写回 world ===")
        writeback(client, results, args.world_id)
    if results and not args.no_download:
        print("\n=== 下载资产到本地缓存 ===")
        download_assets(client, results)

    ok = len(results)
    total = len(args.roles)
    print(f"\n=== 汇总: {ok}/{total} 成功 ===")
    if ok < total:
        failed = [r for r in args.roles if r not in results]
        print(f"  失败: {failed}，可用 --skip-convert --results-file 重试写回")


if __name__ == "__main__":
    main()
