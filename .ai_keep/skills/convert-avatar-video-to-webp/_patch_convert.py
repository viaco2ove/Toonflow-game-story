# -*- coding: utf-8 -*-
"""给 convert.py 打 birefnet_rvm 补丁（幂等：已打过的跳过）"""
from pathlib import Path

p = Path(__file__).parent / "convert.py"
src = p.read_text(encoding="utf-8")

# ---- Patch 1: 常量 ----
if "DEFAULT_RVM_PTH" not in src:
    anchor = 'DEFAULT_BIREFNET_MODEL = DEFAULT_BIREFNET_DIR / "model-cache" / "birefnet-portrait.onnx"\n'
    assert anchor in src, "P1 anchor"
    src = src.replace(anchor, anchor + 'DEFAULT_RVM_PTH = DEFAULT_BIREFNET_DIR / "model-cache" / "rvm_mobilenetv3.pth"\n', 1)
    print("P1 ok: 常量")

# ---- Patch 2: load_config 模型识别 ----
if 'model_is_birefnet_rvm' not in src:
    old2 = '''        model_is_modnet = raw.get("model", "").lower() in ("modnet", "modnet_photographic_portrait_matting")
        model_is_birefnet = raw.get("model", "").lower() in ("birefnet", "birefnet-portrait")

        if model_is_modnet:
            cfg["model"] = "modnet"
        elif model_is_birefnet:
            cfg["model"] = "birefnet-portrait"'''
    new2 = '''        model_val = raw.get("model", "").lower()
        model_is_modnet = model_val in ("modnet", "modnet_photographic_portrait_matting")
        model_is_birefnet_rvm = model_val == "birefnet_rvm"
        model_is_birefnet = model_val in ("birefnet", "birefnet-portrait") or model_is_birefnet_rvm

        if model_is_modnet:
            cfg["model"] = "modnet"
        elif model_is_birefnet_rvm:
            cfg["model"] = "birefnet_rvm"
        elif model_is_birefnet:
            cfg["model"] = "birefnet-portrait"'''
    assert old2 in src, "P2 anchor"
    src = src.replace(old2, new2, 1)
    print("P2 ok: load_config")

# ---- Patch 3: main() 抠图分支 ----
if "use_birefnet_rvm" not in src:
    old3a = '''    use_birefnet = model_name.lower().startswith("birefnet")
    effective_model = birefnet_model if use_birefnet else modnet_model'''
    new3a = '''    use_birefnet = model_name.lower().startswith("birefnet")
    use_birefnet_rvm = model_name.lower() == "birefnet_rvm"
    effective_model = birefnet_model if use_birefnet else modnet_model
    rvm_pth = Path(DEFAULT_RVM_PTH)'''
    assert old3a in src, "P3a anchor"
    src = src.replace(old3a, new3a, 1)

    old3b = '''    if not effective_model.exists():
        print(json.dumps({"ok": False, "error": f"模型不存在: {effective_model}"}), file=sys.stderr)
        return 2'''
    new3b = '''    if not effective_model.exists():
        print(json.dumps({"ok": False, "error": f"模型不存在: {effective_model}"}), file=sys.stderr)
        return 2
    if use_birefnet_rvm and not rvm_pth.exists():
        print(json.dumps({"ok": False, "error": f"RVM 权重不存在: {rvm_pth}"}), file=sys.stderr)
        return 2'''
    assert old3b in src, "P3b anchor"
    src = src.replace(old3b, new3b, 1)

    old3c = '''    first_rgba = None
    completed = 0
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(matte_frame_wrapper, a): a[0] for a in matte_args}
        for future in as_completed(futures):
            idx, rgba_or_path, err = future.result()
            completed += 1
            if err:
                raise RuntimeError(f"帧 {idx} 抠图失败: {err}")
            if idx == 1:
                first_rgba = rgba_or_path
            if completed % 5 == 0 or completed == len(src_frames):
                print(json.dumps({
                    "ok": True, "phase": "matting",
                    "done": completed, "total": len(src_frames),
                    "elapsed_s": round(time.time() - t0, 2)
                }, ensure_ascii=False), file=sys.stderr)

    t_modnet = time.time() - t0'''
    new3c = '''    if use_birefnet_rvm:
        # ---- birefnet_rvm：首帧 BiRefNet 精抠 + RVM recurrent 传播 + EMA 平滑 ----
        worker_script = Path(__file__).parent / "_birefnet_rvm_worker.py"
        if not worker_script.exists():
            print(json.dumps({"ok": False, "error": f"worker 不存在: {worker_script}"}), file=sys.stderr)
            return 2
        proc = subprocess.run(
            [str(python_birefnet), str(worker_script), str(src_dir), str(matte_dir)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        for line in (proc.stderr or "").splitlines():
            line = line.strip()
            if line.startswith("{"):
                print(line, file=sys.stderr)
        if proc.returncode != 0:
            print(json.dumps({"ok": False, "error": f"birefnet_rvm worker 失败: {(proc.stderr or '')[-1200:]}"}),
                  file=sys.stderr)
            return 4
        first_rgba = (matte_dir / "frame_0001.png").read_bytes()
        t_modnet = time.time() - t0
        print(json.dumps({"ok": True, "phase": "matting_done", "total": len(src_frames),
                          "elapsed_s": round(t_modnet, 2), "engine": "birefnet_rvm"},
                         ensure_ascii=False), file=sys.stderr)
    else:
        first_rgba = None
        completed = 0
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = {ex.submit(matte_frame_wrapper, a): a[0] for a in matte_args}
            for future in as_completed(futures):
                idx, rgba_or_path, err = future.result()
                completed += 1
                if err:
                    raise RuntimeError(f"帧 {idx} 抠图失败: {err}")
                if idx == 1:
                    first_rgba = rgba_or_path
                if completed % 5 == 0 or completed == len(src_frames):
                    print(json.dumps({
                        "ok": True, "phase": "matting",
                        "done": completed, "total": len(src_frames),
                        "elapsed_s": round(time.time() - t0, 2)
                    }, ensure_ascii=False), file=sys.stderr)

        t_modnet = time.time() - t0'''
    assert old3c in src, "P3c anchor"
    src = src.replace(old3c, new3c, 1)
    print("P3 ok: main() 分支")

p.write_text(src, encoding="utf-8")
print("convert.py patched, total lines:", len(src.splitlines()))
