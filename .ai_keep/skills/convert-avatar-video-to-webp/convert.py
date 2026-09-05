#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert-avatar-video-to-webp

把 mp4 角色视频头像转成 webp 动画头像 + png 背景。
不走 Toonflow 服务端 /game/convertAvatarVideoToGif，直接在本地用
ffmpeg（抽帧/合成 webp）+ MODNet（onnxruntime 逐帧抠图）做。

用法：
  python convert.py --mp4 in.mp4 --out-dir out/

详见 ../SKILL.md。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# --------- 默认路径定位（Windows 项目内嵌 birefnet venv） ---------

DEFAULT_APP_ROOT = Path(
    r"D:/Users/viaco/tools/Toonflow-game/toonflow-game-app/Toonflow-game"
)
DEFAULT_BIREFNET_DIR = DEFAULT_APP_ROOT / "tools" / "avatar-matting" / "birefnet"
DEFAULT_PYTHON = DEFAULT_BIREFNET_DIR / "venv" / "Scripts" / "python.exe"
DEFAULT_MODNET_MODEL = DEFAULT_BIREFNET_DIR / "model-cache" / "modnet_photographic_portrait_matting.onnx"

# server 端常量（保持对齐）
DEFAULT_GIF_SIDE = 512
DEFAULT_BG_SIDE = 768
DEFAULT_MAX_SECONDS = 4
DEFAULT_FPS = 10

COMMON_WIN_FFMPEG_PATHS = [
    r"D:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe",
    r"D:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
]


# --------- ffmpeg 工具 ---------

def discover_ffmpeg(explicit: str = "") -> str:
    if explicit and Path(explicit).exists():
        return explicit
    env_path = os.environ.get("FFMPEG_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path
    for cand in COMMON_WIN_FFMPEG_PATHS:
        if Path(cand).exists():
            return cand
    # 回退到 where
    try:
        out = subprocess.run(
            ["where", "ffmpeg"], capture_output=True, text=True, check=False
        )
        first = (out.stdout or "").splitlines()
        for line in first:
            line = line.strip()
            if line and Path(line).exists():
                return line
    except Exception:
        pass
    raise FileNotFoundError("未找到 ffmpeg，请安装并加入 PATH，或用 --ffmpeg 指定")


def run_ffmpeg(ffmpeg: str, args: list[str]) -> None:
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *args]
    # Windows 中文路径下 ffmpeg 输出含 GBK 字节，统一用 utf-8 errors=replace 避免崩
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg 失败（exit={proc.returncode}）\n"
            f"命令: {' '.join(cmd)}\n"
            f"stderr: {proc.stderr.strip()[-2000:]}"
        )


# --------- MODNet 内联推理（避免每帧起一次 Python 子进程） ---------

_MODNET_SESSION = None  # 全局缓存 onnxruntime session


def get_modnet_session(model_path: Path):
    global _MODNET_SESSION
    if _MODNET_SESSION is not None:
        return _MODNET_SESSION
    import onnxruntime  # 延迟导入，让 --help 不依赖 venv

    if not model_path.exists():
        raise FileNotFoundError(f"MODNet 模型不存在: {model_path}")
    _MODNET_SESSION = onnxruntime.InferenceSession(str(model_path), None)
    return _MODNET_SESSION


def modnet_rgba(image_path: Path, out_path: Path, model_path: Path) -> None:
    """对单张图片跑 MODNet，输出 RGBA PNG（透明背景）"""
    import numpy as np
    from PIL import Image

    session = get_modnet_session(model_path)
    REF_SIZE = 512

    img = Image.open(image_path).convert("RGB")
    arr = np.asarray(img).astype(np.float32)
    h, w, _ = arr.shape

    # 与 run_modnet.py 保持一致的缩放策略（32 对齐）
    if max(h, w) < REF_SIZE or min(h, w) > REF_SIZE:
        if w >= h:
            rh = REF_SIZE
            rw = int(w / h * REF_SIZE)
        else:
            rw = REF_SIZE
            rh = int(h / w * REF_SIZE)
    else:
        rh, rw = h, w
    rw = max(32, rw - rw % 32)
    rh = max(32, rh - rh % 32)
    x_scale = rw / w
    y_scale = rh / h

    normalized = (arr - 127.5) / 127.5
    resized = Image.fromarray(np.clip(normalized * 127.5 + 127.5, 0, 255).astype(np.uint8)).resize(
        (max(32, int(round(w * x_scale / 32.0) * 32)),
         max(32, int(round(h * y_scale / 32.0) * 32))),
        Image.Resampling.BILINEAR,
    )
    tensor = (np.asarray(resized).astype(np.float32) - 127.5) / 127.5
    tensor = np.transpose(tensor, (2, 0, 1))
    tensor = np.expand_dims(tensor, axis=0).astype("float32")

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    matte = np.squeeze(session.run([output_name], {input_name: tensor})[0])
    matte = np.clip(matte * 255.0, 0, 255).astype("uint8")

    alpha = Image.fromarray(matte, mode="L").resize((w, h), Image.Resampling.BILINEAR)
    rgba = img.convert("RGBA")
    rgba.putalpha(alpha)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out_path, format="PNG")


# --------- 主流程 ---------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="mp4 → foreground.webp + background.png")
    p.add_argument("--mp4", required=True, help="输入 mp4 路径")
    p.add_argument("--out-dir", required=True, help="输出目录")
    p.add_argument("--gif-side", type=int, default=DEFAULT_GIF_SIDE)
    p.add_argument("--bg-side", type=int, default=DEFAULT_BG_SIDE)
    p.add_argument("--fps", type=int, default=DEFAULT_FPS)
    p.add_argument("--max-seconds", type=int, default=DEFAULT_MAX_SECONDS)
    p.add_argument("--python", default=str(DEFAULT_PYTHON), help="Python 解释器（默认用 birefnet venv）")
    p.add_argument("--modnet-model", default=str(DEFAULT_MODNET_MODEL))
    p.add_argument("--ffmpeg", default="", help="ffmpeg 路径（默认自动查找）")
    p.add_argument("--keep-tmp", action="store_true", help="保留中间 PNG 帧用于排查")
    return p.parse_args()


def get_video_duration_ms(ffmpeg: str, mp4: Path) -> int:
    """优先用 ffprobe（结构化输出），回退到 ffmpeg -i 的 stderr 解析。"""
    # 1) ffprobe
    ffprobe = Path(ffmpeg).with_name("ffprobe.exe")
    if ffprobe.exists():
        try:
            proc = subprocess.run(
                [str(ffprobe), "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(mp4)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            val = (proc.stdout or "").strip()
            if val:
                return int(float(val) * 1000)
        except Exception:
            pass

    # 2) ffmpeg stderr 解析
    cmd = [ffmpeg, "-hide_banner", "-i", str(mp4)]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    import re
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr or "")
    if not m:
        return 0
    h, mn, s = m.group(1), m.group(2), m.group(3)
    return int((int(h) * 3600 + int(mn) * 60 + float(s)) * 1000)


def main() -> int:
    args = parse_args()
    mp4 = Path(args.mp4).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not mp4.exists():
        print(json.dumps({"ok": False, "error": f"mp4 不存在: {mp4}"}), file=sys.stderr)
        return 2

    ffmpeg = discover_ffmpeg(args.ffmpeg)
    python = Path(args.python)
    model = Path(args.modnet_model)

    if not python.exists():
        print(json.dumps({"ok": False, "error": f"python 不存在: {python}"}), file=sys.stderr)
        return 2
    if not model.exists():
        print(json.dumps({"ok": False, "error": f"MODNet 模型不存在: {model}"}), file=sys.stderr)
        return 2

    # 1) 复制 video.mp4
    video_out = out_dir / "video.mp4"
    shutil.copy2(mp4, video_out)

    # 2) 抽首帧
    first_frame = out_dir / "firstFrame.png"
    run_ffmpeg(ffmpeg, [
        "-ss", "0", "-i", str(mp4),
        "-vframes", "1", str(first_frame),
    ])

    # 3) 缩放首帧到 bg_side 作为背景
    background = out_dir / "background.png"
    crop_bg = (
        f"scale={args.bg_side}:{args.bg_side}:"
        f"force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={args.bg_side}:{args.bg_side}"
    )
    run_ffmpeg(ffmpeg, [
        "-ss", "0", "-i", str(mp4),
        "-vframes", "1", "-vf", crop_bg, str(background),
    ])

    # 4) 抽帧到临时目录
    tmp_root = out_dir / "_tmp_frames"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    src_dir = tmp_root / "src"
    alpha_dir = tmp_root / "alpha"
    src_dir.mkdir(parents=True, exist_ok=True)
    alpha_dir.mkdir(parents=True, exist_ok=True)

    crop_animated = (
        f"fps={args.fps},"
        f"scale={args.gif_side}:{args.gif_side}:"
        f"force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={args.gif_side}:{args.gif_side},"
        f"format=rgba"
    )
    run_ffmpeg(ffmpeg, [
        "-ss", "0", "-t", str(args.max_seconds),
        "-i", str(mp4),
        "-vf", crop_animated,
        str(src_dir / "frame_%04d.png"),
    ])

    src_frames = sorted(src_dir.glob("frame_*.png"))
    if not src_frames:
        print(json.dumps({"ok": False, "error": "抽帧失败，源目录为空"}), file=sys.stderr)
        return 3

    # 5) MODNet 逐帧抠图
    t0 = time.time()
    for i, src in enumerate(src_frames, 1):
        modnet_rgba(src, alpha_dir / src.name, model)
        if i % 5 == 0 or i == len(src_frames):
            print(f"[modnet] {i}/{len(src_frames)} frames ({time.time() - t0:.1f}s)", file=sys.stderr)
    t_modnet = time.time() - t0

    # 6) ffmpeg 合成 webp
    foreground = out_dir / "foreground.webp"
    run_ffmpeg(ffmpeg, [
        "-framerate", str(args.fps),
        "-i", str(alpha_dir / "frame_%04d.png"),
        "-c:v", "libwebp",
        "-lossless", "0",
        "-q:v", "80",
        "-compression_level", "6",
        "-preset", "picture",
        "-loop", "0",
        "-an",
        str(foreground),
    ])

    duration_ms = get_video_duration_ms(ffmpeg, mp4)
    frames = len(src_frames)

    if not args.keep_tmp:
        shutil.rmtree(tmp_root, ignore_errors=True)

    result = {
        "ok": True,
        "foreground": str(foreground),
        "background": str(background),
        "firstFrame": str(first_frame),
        "video": str(video_out),
        "durationMs": duration_ms,
        "frames": frames,
        "gifSide": args.gif_side,
        "bgSide": args.bg_side,
        "fps": args.fps,
        "modnetSeconds": round(t_modnet, 2),
    }
    # stdout 必须只输出 JSON，方便脚本解析
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
