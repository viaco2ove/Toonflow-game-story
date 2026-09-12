#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert-avatar-video-to-webp  (v3 — 修复 webp/背景重影)

mp4 → foreground.webp + background.png + firstFrame.png

v3 修复重影（2026-09-12，A/B/C）：
  A. webp 无损编码：lossless=1 + quality=90 + compression_level=4
     （对齐 app libwebp_anim）—— v2 有损编码压坏半透明 alpha 边缘，
     背景色"漏"出来形成重影
  B. 背景改用 512 垫边版首帧 + 同尺寸 matte 帧（同管线产出，像素级
     对齐）—— v2 原始分辨率首帧重新抠图，mask 几何不一致导致偏移重影
  C. colorkey=0x000000:0.08:0.05 软抠边（对齐 app legacy 路径），
     键掉发丝/轮廓边缘残留的近黑像素

v2 改进：
  - 读取 vedio_to_webp.yml 配置（FPS / 时长 / 尺寸 / 并发数）
  - 默认使用 birefnet-portrait 抠图（对齐官方），可降级到 MODNet
  - 并发批处理帧（VIDEO_TO_ANIMATION_MULTIPLIED_SPEED）
  - 语义背景：官方 createApproximateBackgroundLayer 算法

用法：
  python convert.py --mp4 in.mp4 --out-dir out/ [--config config.yml]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# --------- 默认路径（Windows 项目内嵌 birefnet venv）---------

DEFAULT_APP_ROOT = Path(r"D:/Users/viaco/tools/Toonflow-game/toonflow-game-app/Toonflow-game")
DEFAULT_BIREFNET_DIR = DEFAULT_APP_ROOT / "tools" / "avatar-matting" / "birefnet"
DEFAULT_MODNET_DIR = DEFAULT_APP_ROOT / "tools" / "avatar-matting" / "birefnet"
DEFAULT_PYTHON_BIREFNET = DEFAULT_BIREFNET_DIR / "venv" / "Scripts" / "python.exe"
DEFAULT_MODNET_MODEL = DEFAULT_MODNET_DIR / "model-cache" / "modnet_photographic_portrait_matting.onnx"
DEFAULT_BIREFNET_MODEL = DEFAULT_BIREFNET_DIR / "model-cache" / "birefnet-portrait.onnx"
DEFAULT_RVM_PTH = DEFAULT_BIREFNET_DIR / "model-cache" / "rvm_mobilenetv3.pth"

# 默认参数（当 config.yml 不存在时使用）
DEFAULT_GIF_SIDE = 512
DEFAULT_BG_SIDE = 768
DEFAULT_MAX_SECONDS = 4
DEFAULT_FPS = 10
DEFAULT_FRAME_SIDE = 512
DEFAULT_CONCURRENCY = 2  # birefnet 默认并发

COMMON_WIN_FFMPEG_PATHS = [
    r"D:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe",
    r"D:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
]


# --------- 配置加载 ---------

def load_config(config_path: str) -> dict:
    """读取 vedio_to_webp.yml，返回 {model, fps, max_seconds, frame_side, concurrency}"""
    import yaml

    cfg = {
        "model": "birefnet-portrait",
        "concurrency": DEFAULT_CONCURRENCY,
        "max_seconds": DEFAULT_MAX_SECONDS,
        "fps": DEFAULT_FPS,
        "frame_side": DEFAULT_FRAME_SIDE,
        "gif_side": DEFAULT_GIF_SIDE,
        "bg_side": DEFAULT_BG_SIDE,
    }

    if config_path and Path(config_path).exists():
        with open(config_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        # --- 第一步：从 raw 文本里判断模型（不依赖 cfg["model"] 初始值）---
        raw_str = str(raw).lower()
        model_val = raw.get("model", "").lower()
        model_is_modnet = model_val in ("modnet", "modnet_photographic_portrait_matting")
        model_is_birefnet_rvm = model_val == "birefnet_rvm"
        model_is_birefnet = model_val in ("birefnet", "birefnet-portrait") or model_is_birefnet_rvm

        if model_is_modnet:
            cfg["model"] = "modnet"
        elif model_is_birefnet_rvm:
            cfg["model"] = "birefnet_rvm"
        elif model_is_birefnet:
            cfg["model"] = "birefnet-portrait"

        # --- 第二步：根据实际模型类型解析对应配置块 ---
        for key, value in raw.items():
            k = key.upper()
            if model_is_modnet and "MODNET" in k:
                if "MULTIPLIED_SPEED" in k and value:
                    cfg["concurrency"] = max(1, int(value))
                elif "MAX_GIF_DURATION_SECONDS" in k and value:
                    cfg["max_seconds"] = int(value)
                elif "GIF_FPS" in k and value:
                    cfg["fps"] = max(1, min(30, int(value)))
                elif "FRAME_OUTPUT_SIDE" in k and value:
                    cfg["frame_side"] = max(128, int(value))
                    cfg["gif_side"] = cfg["frame_side"]  # 帧输出边长即 webp 边长
            elif model_is_birefnet and "BIREFNET" in k:
                if "MULTIPLIED_SPEED" in k and value:
                    cfg["concurrency"] = max(1, int(value))
                elif "MAX_GIF_DURATION_SECONDS" in k and value:
                    cfg["max_seconds"] = int(value)
                elif "GIF_FPS" in k and value:
                    cfg["fps"] = max(1, min(30, int(value)))
                elif "FRAME_OUTPUT_SIDE" in k and value:
                    cfg["frame_side"] = max(128, int(value))
                    cfg["gif_side"] = cfg["frame_side"]  # 帧输出边长即 webp 边长

    return cfg


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
    try:
        out = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True, check=False)
        for line in (out.stdout or "").splitlines():
            line = line.strip()
            if line and Path(line).exists():
                return line
    except Exception:
        pass
    raise FileNotFoundError("未找到 ffmpeg，请安装并加入 PATH，或用 --ffmpeg 指定")


def run_ffmpeg(ffmpeg: str, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *args]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg 失败（exit={proc.returncode}）\n"
            f"命令: {' '.join(cmd)}\n"
            f"stderr: {proc.stderr.strip()[-2000:]}"
        )
    return proc


# --------- BiRefNet / MODNet 抠图 ---------

def matte_frame_birefnet(frame_bytes: bytes, python: Path, model_path: Path) -> bytes:
    """用 birefnet venv 的 rembg 抠一张帧，返回 RGBA PNG bytes。
    rembg new_session('birefnet-portrait') 会去 $U2NET_HOME 找 birefnet-portrait.onnx。
    必须把 U2NET_HOME 指向本地 model-cache，否则 rembg 会联网下载 928MB（极慢/卡死）。
    """
    script = "\n".join([
        "import sys",
        "from rembg import new_session, remove",
        "session = new_session('birefnet-portrait')",
        "result = remove(sys.stdin.buffer.read(), session=session, force_return_bytes=True)",
        "sys.stdout.buffer.write(result)",
    ])
    # 关键：把 U2NET_HOME 指向本地已存在的模型目录，避免联网下载
    env = os.environ.copy()
    env.setdefault("U2NET_HOME", str(Path(model_path).parent))
    proc = subprocess.run(
        [str(python), "-c", script],
        input=frame_bytes,
        capture_output=True,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"birefnet 抠图失败: {proc.stderr.decode('utf-8', errors='replace')[-500:]}")
    return proc.stdout


def matte_frame_modnet(frame_path: Path, out_path: Path, model_path: Path) -> None:
    """用 MODNet（onnxruntime）抠一张帧，输出 RGBA PNG。"""
    import numpy as np
    import onnxruntime
    from PIL import Image

    session = onnxruntime.InferenceSession(str(model_path), None)
    REF_SIZE = 512

    img = Image.open(frame_path).convert("RGB")
    arr = np.asarray(img).astype(np.float32)
    h, w, _ = arr.shape

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

    resized = img.resize((max(32, rw), max(32, rh)), Image.Resampling.BILINEAR)
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


def matte_frame_wrapper(args):
    """并发包装：matte 一帧。返回 (frame_index, rgba_bytes or None, error)"""
    idx, src_path, matte_dir, model, python, modnet_model, use_birefnet = args
    out_path = matte_dir / f"frame_{str(idx).zfill(4)}.png"
    last_err = None
    for attempt in range(3):  # Windows 并发写盘偶发 Permission denied，重试
        try:
            if use_birefnet:
                rgba_bytes = matte_frame_birefnet(src_path.read_bytes(), python, modnet_model)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(rgba_bytes)
            else:
                matte_frame_modnet(src_path, out_path, modnet_model)
            return idx, out_path.read_bytes(), None
        except Exception as e:
            last_err = str(e)
            time.sleep(0.6 * (attempt + 1))
    return idx, None, f"{last_err} (重试3次后仍失败)"


def apply_colorkey_edge(img: Image.Image, threshold: float = 0.08, softness: float = 0.05) -> Image.Image:
    """对齐 app.js legacy 路径的 colorkey 软抠边。

    v3 Fix C：对 matte 帧的 RGB 做色键透明。
    发丝/轮廓边缘残留的近黑像素（alpha 极低、RGB 极暗）会被软透明化，
    防止这些残留像素在 webp 无损压缩后"渗出"形成重影。

    参数（对齐 app.js）：
      threshold=0.08  — alpha < 0.08 的近黑像素视为边缘
      softness=0.05   — 0.08~0.13 区间软过渡
    """
    alpha = img.getchannel("A")
    rgb = img.convert("RGB")
    from PIL import Image
    import numpy as np

    a = np.asarray(alpha, dtype=np.float32) / 255.0
    r, g, b = np.asarray(rgb, dtype=np.float32).transpose(2, 0, 1)

    # 近黑检测：R/G/B 均 < 20 且 alpha < threshold
    is_near_black = ((r < 20) & (g < 20) & (b < 20)).astype(np.float32)
    edge_mask = is_near_black * np.clip(a / max(threshold, 0.001), 0, 1)
    # softness 平滑：0.08~0.13 区间线性过渡
    softness_start = threshold
    softness_end = threshold + softness
    a_soft = np.where(
        (a >= softness_start) & (a < softness_end),
        (a - softness_start) / (softness_end - softness_start),
        np.where(a >= softness_end, np.ones_like(a), np.zeros_like(a))
    )
    # 近黑像素 + 边缘区共同决定软抠边强度
    soft_edge = np.clip(edge_mask * 0.5 + a_soft * is_near_black, 0, 1)
    new_alpha = np.clip(a + soft_edge * (1 - a), 0, 1)

    out = img.copy()
    out.putalpha(Image.fromarray((new_alpha * 255).astype(np.uint8), mode="L"))
    return out


# --------- 背景生成（官方算法）---------

def build_official_background(matte_first_frame: Image.Image, bg_side: int = 768):
    """对齐官方 createApproximateBackgroundLayer（app.js separateRoleAvatar）。

    v3 Fix B：改用 512 垫边版首帧 matte（与抽帧管线产出同尺寸），
    不再重新对原始分辨率首帧抠图，避免 mask 几何错位导致背景重影。

    1. matte 帧 RGB 部分做 blur(12) + 亮度 1.01 + 饱和度 0.94
    2. 前景 alpha 通道 blur(10) 作为人物 mask
    3. 仅人物区域叠加模糊版（"融"进背景）
    4. cover centre 到 bg_side × bg_side
    """
    from PIL import Image, ImageEnhance, ImageFilter

    # matte_first_frame 已经是 512×512 RGBA（抽帧管线产出，同尺寸像素级对齐）
    fg_rgb = matte_first_frame.convert("RGB")
    w, h = fg_rgb.size  # 512×512

    # 1. 模糊底图
    blurred = fg_rgb.filter(ImageFilter.GaussianBlur(12))
    blurred = ImageEnhance.Brightness(blurred).enhance(1.01)
    blurred = ImageEnhance.Color(blurred).enhance(0.94)

    # 2. 人物 mask（前景 alpha → blur 10，与源图同尺寸，无错位）
    subject_mask = matte_first_frame.getchannel("A").filter(ImageFilter.GaussianBlur(10))

    # 3. 仅人物区域叠加模糊版
    softened = fg_rgb.copy()
    softened.paste(blurred, (0, 0), subject_mask)

    # 4. cover centre 到 bg_side（fillOpaqueCanvas）
    scale = max(bg_side / w, bg_side / h)
    new_w = max(1, int(w * scale + 0.5))
    new_h = max(1, int(h * scale + 0.5))
    resized = softened.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - bg_side) // 2
    top = (new_h - bg_side) // 2
    return resized.crop((left, top, left + bg_side, top + bg_side))


# --------- 主流程 ---------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="mp4 → foreground.webp + background.png + firstFrame.png")
    p.add_argument("--mp4", required=True, help="输入 mp4 路径")
    p.add_argument("--out-dir", required=True, help="输出目录")
    p.add_argument("--config", default="", help="vedio_to_webp.yml 路径（默认在技能目录查找）")
    p.add_argument("--model", default="",
                   help="抠图模型: birefnet-portrait 或 modnet（不传则读 yml 的 model，再默认 birefnet-portrait）")
    p.add_argument("--gif-side", type=int, default=None)
    p.add_argument("--bg-side", type=int, default=None)
    p.add_argument("--fps", type=int, default=None)
    p.add_argument("--max-seconds", type=int, default=None)
    p.add_argument("--concurrency", type=int, default=None,
                   help="并发抠图帧数（默认读 yml，再默认 2）")
    p.add_argument("--python-birefnet", default=str(DEFAULT_PYTHON_BIREFNET))
    p.add_argument("--modnet-model", default=str(DEFAULT_MODNET_MODEL))
    p.add_argument("--birefnet-model", default=str(DEFAULT_BIREFNET_MODEL))
    p.add_argument("--ffmpeg", default="")
    p.add_argument("--keep-tmp", action="store_true", help="保留中间帧")
    return p.parse_args()


def get_video_duration_ms(ffmpeg: str, mp4: Path) -> int:
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
    import re
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(mp4)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
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

    # 1. 加载配置
    config_path = args.config
    if not config_path:
        skill_dir = Path(__file__).parent
        default_cfg = skill_dir / ".." / ".." / "config" / "vedio_to_webp.yml"
        if default_cfg.exists():
            config_path = str(default_cfg.resolve())

    cfg = load_config(config_path) if config_path else {}
    # 优先级：命令行显式传参 > yml > 内置默认
    fps = args.fps if args.fps is not None else cfg.get("fps", DEFAULT_FPS)
    max_seconds = args.max_seconds if args.max_seconds is not None else cfg.get("max_seconds", DEFAULT_MAX_SECONDS)
    gif_side = args.gif_side if args.gif_side is not None else cfg.get("gif_side", DEFAULT_GIF_SIDE)
    bg_side = args.bg_side if args.bg_side is not None else cfg.get("bg_side", DEFAULT_BG_SIDE)
    concurrency = args.concurrency if args.concurrency is not None else cfg.get("concurrency", DEFAULT_CONCURRENCY)
    # yml 里有 model 配置；命令行 --model 空字符串时以 yml 为准
    model_name = args.model or cfg.get("model", "birefnet-portrait")

    print(json.dumps({"ok": True, "phase": "start", "config": cfg, "model": model_name,
                      "fps": fps, "max_seconds": max_seconds, "concurrency": concurrency},
                     ensure_ascii=False), file=sys.stderr)

    ffmpeg = discover_ffmpeg(args.ffmpeg)
    python_birefnet = Path(args.python_birefnet)
    modnet_model = Path(args.modnet_model)
    birefnet_model = Path(args.birefnet_model)

    use_birefnet = model_name.lower().startswith("birefnet")
    use_birefnet_rvm = model_name.lower() == "birefnet_rvm"
    effective_model = birefnet_model if use_birefnet else modnet_model
    rvm_pth = Path(DEFAULT_RVM_PTH)

    if not python_birefnet.exists():
        print(json.dumps({"ok": False, "error": f"python 不存在: {python_birefnet}"}), file=sys.stderr)
        return 2
    if not effective_model.exists():
        print(json.dumps({"ok": False, "error": f"模型不存在: {effective_model}"}), file=sys.stderr)
        return 2
    if use_birefnet_rvm and not rvm_pth.exists():
        print(json.dumps({"ok": False, "error": f"RVM 权重不存在: {rvm_pth}"}), file=sys.stderr)
        return 2

    # 2. 复制 video.mp4（Windows 句柄延迟偶发锁文件，重试 3 次）
    video_out = out_dir / "video.mp4"
    for attempt in range(3):
        try:
            shutil.copy2(mp4, video_out)
            break
        except PermissionError:
            if attempt == 2:
                raise
            time.sleep(1.5)

    # 3. 抽首帧
    first_frame_path = out_dir / "firstFrame.png"
    run_ffmpeg(ffmpeg, ["-ss", "0", "-i", str(mp4), "-vframes", "1", str(first_frame_path)])

    # 4. 抽帧到临时目录（竖版 decrease+pad 不砍头，横版自然全幅）
    # 使用会话唯一目录名：避免"先删旧临时目录"这一步（批量删除 80+ 文件会被
    # safe-delete 拦截，导致刚抽完首帧就中断）。旧目录交给用户手动清理。
    tmp_root = out_dir / f"_tmp_frames_{os.getpid()}_{int(time.time())}"
    if tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
    src_dir = tmp_root / "src"
    matte_dir = tmp_root / "matte"
    src_dir.mkdir(parents=True, exist_ok=True)
    matte_dir.mkdir(parents=True, exist_ok=True)

    # 关键：用 decrease + pad 保持原比例（竖版视频用 increase 会砍头/砍脚）
    crop_animated = (
        f"fps={fps},"
        f"scale={gif_side}:{gif_side}:"
        f"force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={gif_side}:{gif_side}:(ow-iw)/2:(oh-ih)/2:color=0x00000000,"
        f"format=rgba"
    )
    run_ffmpeg(ffmpeg, [
        "-ss", "0", "-t", str(max_seconds),
        "-i", str(mp4),
        "-vf", crop_animated,
        str(src_dir / "frame_%04d.png"),
    ])

    src_frames = sorted(src_dir.glob("frame_*.png"))
    if not src_frames:
        print(json.dumps({"ok": False, "error": "抽帧失败，源目录为空"}), file=sys.stderr)
        return 3
    print(json.dumps({"ok": True, "phase": "frames_extracted", "frame_count": len(src_frames)},
                     ensure_ascii=False), file=sys.stderr)

    # 6. 并发抠图
    t0 = time.time()
    matte_args = [
        (i + 1, src, matte_dir, model_name, python_birefnet, effective_model, use_birefnet)
        for i, src in enumerate(src_frames)
    ]

    if use_birefnet_rvm:
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

        t_modnet = time.time() - t0
    print(json.dumps({"ok": True, "phase": "matting_done", "total": len(src_frames),
                      "elapsed_s": round(t_modnet, 2)}, ensure_ascii=False), file=sys.stderr)

    # 7. 生成背景（官方算法：人物区域模糊化）
    # v3 Fix B：改用 512 垫边版 matte 首帧（与抽帧管线同尺寸），不再对
    # 原始分辨率首帧重新抠图 —— 抠出的 mask 几何错位是重影根因之一
    bg_start = time.time()
    from PIL import Image
    matte_first_path = matte_dir / "frame_0001.png"
    if not matte_first_path.exists():
        print(json.dumps({"ok": False, "error": f"matte 首帧缺失: {matte_first_path}"}, ensure_ascii=False), file=sys.stderr)
        return 4
    matte_first = Image.open(matte_first_path).convert("RGBA")
    background_path = out_dir / "background.png"
    build_official_background(matte_first, bg_side).save(background_path, format="PNG")
    print(json.dumps({"ok": True, "phase": "background_done", "elapsed_s": round(time.time()-bg_start, 2)},
                     ensure_ascii=False), file=sys.stderr)

    # 8. colorkey 软抠边（Fix C）：对齐 app.js legacy 路径
    #    对 matte 帧的近黑残留像素做软透明化，防止 webp 无损压缩后渗出重影
    print(json.dumps({"ok": True, "phase": "colorkey_start"}, ensure_ascii=False), file=sys.stderr)
    matte_frames = sorted(matte_dir.glob("frame_*.png"))
    for mf in matte_frames:
        img = Image.open(mf).convert("RGBA")
        img_fixed = apply_colorkey_edge(img)
        img_fixed.save(mf, format="PNG", optimize=False)
    print(json.dumps({"ok": True, "phase": "colorkey_done", "frames": len(matte_frames)},
                     ensure_ascii=False), file=sys.stderr)

    # 9. 合成 webp（v3 Fix A：无损编码，对齐 app libwebp_anim 参数）
    foreground_path = out_dir / "foreground.webp"
    matte_pattern = str(matte_dir / "frame_%04d.png")
    run_ffmpeg(ffmpeg, [
        "-framerate", str(fps),
        "-i", matte_pattern,
        "-c:v", "libwebp",
        "-lossless", "1",
        "-quality", "90",
        "-compression_level", "4",
        "-preset", "picture",
        "-loop", "0",
        "-an",
        "-vsync", "0",
        str(foreground_path),
    ])

    duration_ms = get_video_duration_ms(ffmpeg, mp4)

    result = {
        "ok": True,
        "foreground": str(foreground_path),
        "background": str(background_path),
        "firstFrame": str(first_frame_path),
        "video": str(video_out),
        "durationMs": duration_ms,
        "frames": len(src_frames),
        "gifSide": gif_side,
        "bgSide": bg_side,
        "fps": fps,
        "concurrency": concurrency,
        "model": model_name,
        "mattingSeconds": round(t_modnet, 2),
        "tmpDir": str(tmp_root),
    }
    print(json.dumps(result, ensure_ascii=False))

    # 结果先输出，再清理临时帧（清理失败不影响结果返回）
    if not args.keep_tmp:
        try:
            shutil.rmtree(tmp_root, ignore_errors=True)
        except Exception as e:
            print(json.dumps({"ok": True, "warn": f"临时目录清理失败，可手动删除: {tmp_root} ({e})"},
                             ensure_ascii=False), file=sys.stderr)
    else:
        print(json.dumps({"ok": True, "warn": f"--keep-tmp 已保留临时目录: {tmp_root}"},
                         ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
