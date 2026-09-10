"""birefnet_rvm 抠图 worker（在 birefnet venv 中运行）。

管线：
  1. 首帧 rembg[birefnet-portrait] 精抠（发丝级 alpha）
  2. 全序列喂 RVM（mobilenetv3）建立 recurrent state —— 时序连贯
  3. 首帧输出 = BiRefNet alpha；后续帧输出 = RVM alpha
  4. 帧间 EMA 平滑（0.85 当前 + 0.15 上一帧）压残余抖动
输出：matte_dir/frame_%04d.png（RGBA 透明背景）
用法：python _birefnet_rvm_worker.py <src_dir> <matte_dir> [--ema 0.85] [--dsr 0.25]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

RVM_SRC = r"D:/Users/viaco/tools/Toonflow-game/toonflow-game-app/Toonflow-game/tools/avatar-matting/birefnet/rvm-src"
RVM_PTH = r"D:/Users/viaco/tools/Toonflow-game/toonflow-game-app/Toonflow-game/tools/avatar-matting/birefnet/model-cache/rvm_mobilenetv3.pth"

MODEL_CACHE = Path(RVM_PTH).parent

# 关键：rembg 默认去 ~/.u2net 找 onnx，找不到就会联网下载 928MB（极慢/卡死）。
# 这里把 U2NET_HOME 指向本地已存在的 model-cache，直接复用本地权重，零下载。
os.environ.setdefault("U2NET_HOME", str(MODEL_CACHE))

sys.path.insert(0, RVM_SRC)

import numpy as np
import torch
from PIL import Image

from model import MattingNetwork


def log(obj):
    print(json.dumps(obj, ensure_ascii=False), file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_dir")
    ap.add_argument("matte_dir")
    ap.add_argument("--ema", type=float, default=0.85, help="帧间 EMA 系数（当前帧权重）")
    ap.add_argument("--dsr", type=float, default=0.75,
                    help="RVM downsample_ratio。512px 输入必须 >=0.5（缩小后特征图需维持 256px+），"
                         "0.25 会因细节丢失产生静态背景残影（实测半透 5.2%% -> 0.75 时 1.87%%）")
    args = ap.parse_args()

    src_dir = Path(args.src_dir)
    matte_dir = Path(args.matte_dir)
    matte_dir.mkdir(parents=True, exist_ok=True)
    frames = sorted(src_dir.glob("frame_*.png"))
    if not frames:
        log({"ok": False, "error": f"src_dir 无帧: {src_dir}"})
        return 2

    t0 = time.time()

    # ---- 1. 首帧 BiRefNet 精抠 ----
    local_onnx = MODEL_CACHE / "birefnet-portrait.onnx"
    if not local_onnx.exists():
        log({"ok": False,
             "error": f"本地 BiRefNet 权重缺失: {local_onnx}（rembg 会尝试联网下载，已中止）",
             "u2net_home": str(MODEL_CACHE)})
        return 3
    log({"ok": True, "phase": "using_local_onnx", "path": str(local_onnx),
         "size_mb": round(local_onnx.stat().st_size / 1024 / 1024, 1)})

    from rembg import new_session, remove
    rembg_session = new_session("birefnet-portrait")
    first_bytes = remove(frames[0].read_bytes(), session=rembg_session, force_return_bytes=True)
    first_rgba = Image.open(__import__("io").BytesIO(first_bytes)).convert("RGBA")
    log({"ok": True, "phase": "birefnet_first_frame", "elapsed_s": round(time.time() - t0, 2)})

    # ---- 2. RVM 时序传播 ----
    model = MattingNetwork("mobilenetv3").eval()
    model.load_state_dict(torch.load(RVM_PTH, map_location="cpu", weights_only=True))
    rec = [None] * 4
    torch.set_num_threads(max(1, torch.get_num_threads()))

    first_alpha = np.asarray(first_rgba.getchannel("A"), dtype=np.float32) / 255.0
    prev_alpha = first_alpha
    h, w = first_alpha.shape

    t_rvm = time.time()
    for i, fp in enumerate(frames):
        img = Image.open(fp).convert("RGB")
        if img.size != (w, h):
            img = img.resize((w, h), Image.Resampling.BILINEAR)
        src_t = torch.from_numpy(np.asarray(img)).permute(2, 0, 1)[None].float() / 255.0

        with torch.no_grad():
            fgr, pha, *rec = model(src_t, *rec, downsample_ratio=args.dsr)

        rvm_alpha = pha[0, 0].numpy()
        if i == 0:
            alpha = first_alpha  # 首帧用 BiRefNet 精抠结果
        else:
            alpha = args.ema * rvm_alpha + (1 - args.ema) * prev_alpha
        prev_alpha = alpha

        rgba = img.convert("RGBA")
        rgba.putalpha(Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8), mode="L"))
        out = matte_dir / f"frame_{str(i + 1).zfill(4)}.png"
        rgba.save(out, format="PNG")

        if (i + 1) % 10 == 0 or i + 1 == len(frames):
            log({"ok": True, "phase": "rvm", "done": i + 1, "total": len(frames),
                 "elapsed_s": round(time.time() - t_rvm, 2)})

    log({"ok": True, "phase": "done", "frames": len(frames),
         "total_s": round(time.time() - t0, 2)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
