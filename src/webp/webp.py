"""
单个角色的立绘的完整步骤
python -m src.cli webp --living {config} {path_json}
python -m src.cli webp --inanimate {config} {path_json}

config 就是配置文件，如 .workbuddy/config/vedio_to_webp.yml
path_json 就是 生图json 入参。如
npc
{
"input_video":.cache/character/通天传授-收徒系统/墨老/墨老_立绘微动.mp4",
"rolename":"墨老",
"rolenType":"npc",
"story":"通天传授-收徒系统",
"type":"living",
"output_path":".cache/character/通天传授-收徒系统/墨老/webp/"
}
用户
{
"input_video":.cache/character/通天传授-收徒系统/陆川/陆川_立绘微动.mp4",
"rolename":"陆川",
"rolenType":"player",
"story":"通天传授-收徒系统",
"type":"living",
"output_path":".cache/character/通天传授-收徒系统/陆川/webp/"
}

分步操作：视频-》抽帧 -》背景-》首帧-》webp文件-》webp.json
# video.mp4 到 .cache/character/{story}/{rolename}/webp/video.mp4
python -m src.cli webp --living --video.mp4 {config} {path_json}
# 抽帧 到 .cache/character/{story}/{rolename}/webp/_tmp_frames
python -m src.cli webp --living --tmp_frames {config} {path_json}
# 生成背景图片到 到 .cache/character/{story}/{rolename}/webp/background.png
python -m src.cli webp --living --background {config} {path_json}
# 生成首帧图片到 到 .cache/character/{story}/{rolename}/webp/firstFrame.png
python -m src.cli webp --living --firstFrame {config} {path_json}
# 生成抠图后的webp到 .cache/character/{story}/{rolename}/webp/foreground.webp
python -m src.cli webp --living --foreground.webp {config} {path_json}

python -m src.cli webp --living --webp.json {config} {path_json}


================================================================================
入参
================================================================================

{config}     配置文件路径，如 .workbuddy/config/vedio_to_webp.yml
             （相对路径按项目根 Toonflow-game-story/ 解析）

{path_json}  生图 json 入参路径，内容如：
             {
               "input_video": ".cache/character/通天传授-收徒系统/墨老/墨老_立绘微动.mp4",
               "rolename": "墨老",
               "story": "通天传授-收徒系统",
               "type": "living",
               "output_path": ".cache/character/通天传授-收徒系统/墨老/webp/"
             }

             type: living（生物立绘，读 yml 的 model + *_MODNet/*_BIREFNET 配置块）
                 / inanimate（非生物，读 yml 的 model_inanimate + *_INANIMATE 配置块）
             可选字段 normalize_mode: global（默认）/ per-frame

================================================================================
步骤与依赖
================================================================================

  1 --video.mp4       input_video          → video.mp4
  2 --tmp_frames      input_video          → _tmp_frames/src/   （ffmpeg 抽帧）
                                           → _tmp_frames/matte/ （逐帧抠图，raw）
  3 --background      _tmp_frames/{src,matte} 首帧 → background.png
  4 --firstFrame      input_video          → firstFrame.png
  5 --foreground.webp _tmp_frames/matte    → _tmp_frames/norm/ → foreground.webp
  6 --webp.json       以上产物             → webp.json

  不带步骤参数时（python -m src.cli webp --living {config} {path_json}）按 1→6
  顺序跑完整流程。分步执行时 --living / --inanimate 同样要带上：它决定读 yml 的
  哪一组配置块。

⚠️ background 必须在 foreground.webp 之前：background 要的是 **raw** matte 的
   alpha（未 normalize）。本模块把 normalize 结果单独写到 _tmp_frames/norm/，
   不原地改写 matte/，所以任何单步都可以反复重跑，结果一致（幂等）。

================================================================================
重影 / 漂移：两处已定案的根因修复，不可改
================================================================================

1. webp 编码器必须 `-c:v libwebp_anim`
   Animated WebP 每个 ANMF 帧头有 disposal（0=NONE 保留上一帧画布 / 1=BACKGROUND
   先清成透明）与 blending（BLEND alpha 混合 / NO_BLEND 覆写）两位，规范默认
   disposal=0 + BLEND —— 新帧里 alpha=0 的像素不清画布，而是"露出上一帧" → 拖影。
   ffmpeg 两条 webp 动画输出路径：
     -c:v libwebp      → libavformat/webpenc.c 手拼 ANMF，disposal 硬编码 0
                         （FFmpeg ticket #7941，webpenc.c:137 avio_w8(s->pb,0)
                         应为 0x1，挂 7 年未修）→ **必然重影**
     -c:v libwebp_anim → 交给 libwebp 官方 WebPAnimEncoder，逐帧算子矩形 +
                         dispose/blend，保证解码结果 == 输入 → **不重影**
   参数与 app renderSemanticAvatarAssets 逐项一致（不加 -preset）：
     -c:v libwebp_anim -lossless 1 -quality 90 -compression_level 4 -loop 0 -an -vsync 0
   `-lossless 1` 不是画质选项，而是帧间差分可逆性的前提（lossy 下
   IncreaseTransparency + BLEND 会累积漂移出淡残影）。
   启动即 assert_webp_anim_encoder()：ffmpeg 不带该编码器直接报错，绝不静默
   回退到 -c:v libwebp 产出带拖影的 webp。
   不做 alpha 二值化、不做 colorkey 软抠边 —— app 都没有，加了只会把发丝软边
   打成硬锯齿，而且治不好重影。

2. normalize 几何必须全局统一（默认 normalize_mode=global）
   app 的 matteVideoFrame 对**每一帧**单独调 normalizeForegroundLayer，每帧按
   自己的不透明 bbox 重新 裁切→缩放→水平居中+底对齐。微动视频里 bbox 逐帧变化：
   宽高变→scale 脉动；中心变→真实位移被"拉回"；底边变→整体上下推；mask 丢块时
   bbox 突变会让主体疾飞几十像素。这是 app 自身缺陷，照抄会一起继承。
   本模块先求所有 matte 帧 bbox 的**并集**，算一次 crop/scale/paste，再用同一套
   几何刷所有帧 → 帧间真实微动保留，但不再整体漂移；background 与 foreground
   共用同源几何，叠加不错位。
   per-frame 仅作复现 app 行为的对照（会抖）。

严格按照配置文件进行转换，不允许自己改模型。
"""
from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

# 项目根：src/webp/webp.py → Toonflow-game-story/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# --------- 默认路径（Windows 项目内嵌 birefnet venv）---------

DEFAULT_APP_ROOT = Path(r"D:/Users/viaco/tools/Toonflow-game/toonflow-game-app/Toonflow-game")
DEFAULT_BIREFNET_DIR = DEFAULT_APP_ROOT / "tools" / "avatar-matting" / "birefnet"
DEFAULT_PYTHON_BIREFNET = DEFAULT_BIREFNET_DIR / "venv" / "Scripts" / "python.exe"
DEFAULT_MODEL_CACHE = DEFAULT_BIREFNET_DIR / "model-cache"
DEFAULT_MODNET_MODEL = DEFAULT_MODEL_CACHE / "modnet_photographic_portrait_matting.onnx"
DEFAULT_BIREFNET_MODEL = DEFAULT_MODEL_CACHE / "birefnet-portrait.onnx"
DEFAULT_RVM_PTH = DEFAULT_MODEL_CACHE / "rvm_mobilenetv3.pth"

# birefnet_rvm 的 worker（首帧 BiRefNet 精抠 + RVM 传播 + EMA）候选位置
RVM_WORKER_CANDIDATES = [
    PROJECT_ROOT / "src" / "webp" / "_birefnet_rvm_worker.py",
    PROJECT_ROOT / ".workbuddy" / "skills" / "convert-avatar-video-to-webp" / "_birefnet_rvm_worker.py",
    PROJECT_ROOT / ".workbuddy" / "skills" / "convert-avatar-video-to-webp" / "laji" / "_birefnet_rvm_worker.py",
    PROJECT_ROOT / ".ai_keep" / "skills" / "convert-avatar-video-to-webp" / "_birefnet_rvm_worker.py",
]

# 默认参数（config.yml 缺失或缺字段时使用）
DEFAULT_GIF_SIDE = 512
DEFAULT_BG_SIDE = 768
DEFAULT_MAX_SECONDS = 4
DEFAULT_FPS = 10
DEFAULT_FRAME_SIDE = 512
DEFAULT_CONCURRENCY = 2

COMMON_WIN_FFMPEG_PATHS = [
    r"D:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe",
    r"D:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
]

# 对齐 app 的 normalizeForegroundLayer（separateRoleAvatar.ts L307）
AVATAR_STD_SIZE = 512
FOREGROUND_SIDE_PADDING = 10
FOREGROUND_TOP_PADDING = 8
FOREGROUND_BOTTOM_PADDING = 0
# 对齐 app extractOpaqueBounds：ALPHA_CROP_PADDING=6，alpha<=14 一律当透明
ALPHA_CROP_PADDING = 6
ALPHA_OPAQUE_THRESHOLD = 14

STEP_ALIASES = {
    "living": "living",
    "inanimate": "inanimate",
    "video": "video",
    "video.mp4": "video",
    "tmp_frames": "tmp_frames",
    "background": "background",
    "firstFrame": "firstFrame",
    "firstframe": "firstFrame",
    "foreground": "foreground",
    "foreground.webp": "foreground",
    "webp_json": "webp_json",
    "webp.json": "webp_json",
}

# 顺序：视频 → 抽帧 → 背景 → 首帧 → webp 文件 → webp.json
FULL_PIPELINE = ["video", "tmp_frames", "background", "firstFrame", "foreground", "webp_json"]


# --------- 日志 ---------

def log(**payload) -> None:
    """结构化进度日志 → stderr（stdout 只留最终 JSON，方便脚本化调用）。"""
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr, flush=True)


class WebpError(RuntimeError):
    """流程内可预期的失败（缺产物 / 缺依赖 / 入参错）。"""


# --------- 入参解析 ---------

def resolve_path(raw: str | Path, base: Path = PROJECT_ROOT) -> Path:
    """相对路径按项目根解析；绝对路径原样返回。"""
    p = Path(str(raw).strip().strip('"'))
    if not p.is_absolute():
        p = base / p
    return p.resolve()


def load_task_json(path_json: str | Path) -> dict:
    """读生图 json 入参，校验必填字段，把路径解析成绝对路径。"""
    jp = resolve_path(path_json)
    if not jp.exists():
        raise WebpError(f"path_json 不存在: {jp}")
    try:
        raw = json.loads(jp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise WebpError(f"path_json 不是合法 JSON: {jp}\n{e}") from e
    if not isinstance(raw, dict):
        raise WebpError(f"path_json 顶层必须是对象: {jp}")

    missing = [k for k in ("input_video", "rolename", "story", "output_path") if not raw.get(k)]
    if missing:
        raise WebpError(f"path_json 缺字段 {missing}: {jp}")

    task_type = str(raw.get("type", "living")).strip().lower()
    if task_type not in ("living", "inanimate"):
        raise WebpError(f"path_json.type 只能是 living / inanimate，当前: {raw.get('type')!r}")

    normalize_mode = str(raw.get("normalize_mode", "global")).strip().lower()
    if normalize_mode not in ("global", "per-frame"):
        raise WebpError(f"path_json.normalize_mode 只能是 global / per-frame，当前: {normalize_mode!r}")

    input_video = resolve_path(raw["input_video"])
    if not input_video.exists():
        raise WebpError(f"input_video 不存在: {input_video}")

    return {
        "json_path": jp,
        "input_video": input_video,
        "rolename": str(raw["rolename"]),
        "story": str(raw["story"]),
        "type": task_type,
        "output_path": resolve_path(raw["output_path"]),
        "normalize_mode": normalize_mode,
    }


# --------- 配置加载（vedio_to_webp.yml）---------

def load_webp_config(config_path: str | Path, model_class: str = "portrait") -> dict:
    """读 vedio_to_webp.yml，返回 {model, fps, max_seconds, frame_side, gif_side, bg_side,
    concurrency, model_cache}。

    model_class: 'portrait'（生物立绘，读 model + *_MODNet / *_BIREFNET 配置块）
               / 'inanimate'（非生物，读 model_inanimate + *_INANIMATE 配置块）

    严格按配置文件取值，代码内不改模型。
    """
    import yaml

    cfg = {
        "model": "birefnet-portrait",
        "concurrency": DEFAULT_CONCURRENCY,
        "max_seconds": DEFAULT_MAX_SECONDS,
        "fps": DEFAULT_FPS,
        "frame_side": DEFAULT_FRAME_SIDE,
        "gif_side": DEFAULT_GIF_SIDE,
        "bg_side": DEFAULT_BG_SIDE,
        "model_cache": DEFAULT_MODEL_CACHE,
    }

    cp = resolve_path(config_path)
    if not cp.exists():
        raise WebpError(f"config 配置文件不存在: {cp}")

    with open(cp, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    is_inanimate = (model_class == "inanimate")

    # --- 第一步：判定模型（不依赖 cfg["model"] 初始值）---
    model_val = str(raw.get("model", "")).strip().lower()
    model_is_modnet = model_val in ("modnet", "modnet_photographic_portrait_matting")
    model_is_birefnet_rvm = model_val == "birefnet_rvm"
    model_is_birefnet = model_val in ("birefnet", "birefnet-portrait") or model_is_birefnet_rvm

    if is_inanimate:
        cfg["model"] = str(raw.get("model_inanimate", "u2net")).strip().lower()
    elif model_is_modnet:
        cfg["model"] = "modnet"
    elif model_is_birefnet_rvm:
        cfg["model"] = "birefnet_rvm"
    elif model_is_birefnet:
        cfg["model"] = "birefnet-portrait"

    # --- 第二步：按实际模型类型解析对应配置块 ---
    for key, value in raw.items():
        k = str(key).upper()
        if is_inanimate and "INANIMATE" in k:
            _apply_block(cfg, k, value)
        elif not is_inanimate and model_is_modnet and "MODNET" in k:
            _apply_block(cfg, k, value)
        elif not is_inanimate and model_is_birefnet and "BIREFNET" in k:
            _apply_block(cfg, k, value)

    # --- 第三步：model_cache（{DATA_DIR} 占位；DATA_DIR: auto 用内置 app 的 tools 目录）---
    # yml 里写的是 "{DATA_DIR}\\avatar-matting\\birefnet\\model-cache"，而模型实际在
    # <app>/tools/avatar-matting/...，所以 auto 的基准是 <app>/tools 而不是 <app>。
    data_dir_raw = str(raw.get("DATA_DIR", "auto")).strip()
    if data_dir_raw.lower() in ("", "auto"):
        data_dir = str(DEFAULT_APP_ROOT / "tools")
    else:
        data_dir = data_dir_raw
    mc_raw = str(raw.get("model_cache", "")).strip()
    if mc_raw:
        cfg["model_cache"] = Path(mc_raw.replace("{DATA_DIR}", data_dir)).resolve()

    cfg["config_path"] = cp
    return cfg


def _apply_block(cfg: dict, key_upper: str, value) -> None:
    """把 *_MODNet / *_BIREFNET / *_INANIMATE 配置块的一项写进 cfg。"""
    if value in (None, ""):
        return
    if "MULTIPLIED_SPEED" in key_upper:
        cfg["concurrency"] = max(1, int(value))
    elif "MAX_GIF_DURATION_SECONDS" in key_upper:
        cfg["max_seconds"] = int(value)
    elif "GIF_FPS" in key_upper:
        cfg["fps"] = max(1, min(30, int(value)))
    elif "FRAME_OUTPUT_SIDE" in key_upper:
        cfg["frame_side"] = max(128, int(value))
        cfg["gif_side"] = cfg["frame_side"]  # 帧输出边长即 webp 边长


# --------- ffmpeg ---------

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
    except OSError:
        pass
    raise WebpError("未找到 ffmpeg，请安装并加入 PATH，或设置 FFMPEG_PATH 环境变量")


def run_ffmpeg(ffmpeg: str, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and proc.returncode != 0:
        raise WebpError(
            f"ffmpeg 失败（exit={proc.returncode}）\n"
            f"命令: {' '.join(cmd)}\n"
            f"stderr: {proc.stderr.strip()[-2000:]}"
        )
    return proc


def assert_webp_anim_encoder(ffmpeg: str) -> None:
    """确认 ffmpeg 带 libwebp_anim 编码器。

    必须硬失败：一旦回退到 -c:v libwebp，ANMF 的 disposal 会被 ffmpeg 硬编码为
    0(NONE)，透明帧露出上一帧 → 重影。宁可报错，不能静默产出带拖影的 webp。
    """
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-h", "encoder=libwebp_anim"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if "Encoder libwebp_anim" not in (proc.stdout or ""):
        raise WebpError(
            f"当前 ffmpeg 不带 libwebp_anim 编码器：{ffmpeg}\n"
            "必须使用 --enable-libwebp 构建的 ffmpeg（官方 win64-gpl-shared 构建已包含）。\n"
            "不能回退到 -c:v libwebp：那条路径会把 ANMF disposal 硬编码为 0(NONE)，"
            "必然产生重影（FFmpeg ticket #7941）。"
        )


def patch_anmf_disposal_background(webp_path: Path) -> int:
    """把 webp 产物里所有 ANMF 的 disposal 位（flags byte 的 bit0）置为 BACKGROUND(1)。

    背景：libwebp_anim 在主体位置固定的场景下，会省略 BACKGROUND disposal（全 NONE），
    只依赖 NO_BLEND 覆写。遇到不尊重 NO_BLEND 的播放器就会残影单调累积。
    本函数只改 ANMF header 第 16 字节的 bit0，不触碰任何像素数据，文件大小不变。

    安全性：
      - 严格解码器：覆写 + 清空同矩形 + 下一帧再覆写 → 视觉结果与 NONE 完全一致
      - 宽容解码器：BACKGROUND 提供兜底清理，消除残影
      - 末帧置 BACKGROUND 还能让循环回绕时画布归零，避免跨循环残留

    返回被改写的帧数。
    """
    data = bytearray(webp_path.read_bytes())
    pos, patched = 12, 0
    while pos + 8 <= len(data):
        fc = bytes(data[pos:pos + 4])
        sz = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        if fc == b"ANMF":
            flag_off = pos + 8 + 15
            before = data[flag_off]
            data[flag_off] = before | 0x01
            if data[flag_off] != before:
                patched += 1
        pos += 8 + sz + (sz & 1)
    if patched:
        webp_path.write_bytes(bytes(data))
    return patched


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
        except (OSError, ValueError):
            pass
    import re
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(mp4)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr or "")
    if not m:
        return 0
    h, mn, s = m.group(1), m.group(2), m.group(3)
    return int((int(h) * 3600 + int(mn) * 60 + float(s)) * 1000)


# --------- 抠图 ---------

def matte_frame_rembg(frame_bytes: bytes, python: Path, model_name: str, model_dir: Path) -> bytes:
    """用 birefnet venv 的 rembg 抠一张帧，返回 RGBA PNG bytes。

    rembg new_session(<model_name>) 会去 $U2NET_HOME 找对应 .onnx，
    model_name 形如 'birefnet-portrait' / 'u2net' / 'u2netp' / 'isnet-general-use'。
    U2NET_HOME 必须指向本地 model-cache，否则 rembg 会联网下载 928MB（极慢、会挂死）。

    alpha_matting=False：rembg 默认开启 alpha_matting，会把边缘像素 RGB 与背景黑色
    混合（实测 B 通道被压低 22%，边缘偏黑）。关掉以保留模型原始 RGB。
    """
    script = "\n".join([
        "import sys",
        "from rembg import new_session, remove",
        f"session = new_session('{model_name}')",
        "result = remove(sys.stdin.buffer.read(), session=session, force_return_bytes=True, alpha_matting=False)",
        "sys.stdout.buffer.write(result)",
    ])
    env = os.environ.copy()
    env["U2NET_HOME"] = str(model_dir)
    proc = subprocess.run([str(python), "-c", script], input=frame_bytes, capture_output=True, env=env)
    if proc.returncode != 0:
        raise WebpError(f"rembg({model_name}) 抠图失败: {proc.stderr.decode('utf-8', errors='replace')[-500:]}")
    return proc.stdout


def matte_frame_modnet(frame_path: Path, out_path: Path, model_path: Path) -> None:
    """用 MODNet（onnxruntime）抠一张帧，输出 RGBA PNG。"""
    import onnxruntime

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


def matte_frame_wrapper(job: tuple):
    """并发包装：抠一帧。返回 (idx, ok, error)

    job: (idx, src_path, matte_dir, python, model_path, use_rembg, model_name, model_dir)
    """
    idx, src_path, matte_dir, python, model_path, use_rembg, model_name, model_dir = job
    out_path = matte_dir / f"frame_{str(idx).zfill(4)}.png"
    last_err = None
    for attempt in range(3):  # Windows 并发写盘偶发 Permission denied，重试
        try:
            if use_rembg:
                rgba_bytes = matte_frame_rembg(src_path.read_bytes(), python, model_name, model_dir)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(rgba_bytes)
            else:
                matte_frame_modnet(src_path, out_path, model_path)
            return idx, True, None
        except Exception as e:  # noqa: BLE001 — 重试后统一上报
            last_err = str(e)
            time.sleep(0.6 * (attempt + 1))
    return idx, False, f"{last_err} (重试3次后仍失败)"


# --------- 前景几何 ---------

def extract_opaque_bounds(img: Image.Image) -> tuple[int, int, int, int] | None:
    """找不透明像素外接矩形，返回 (left, top, width, height) 或 None（全透明）。

    对齐 app extractOpaqueBounds：alpha<=14 视为透明（滤掉抠图模型残留的极低
    alpha 光晕），外扩 ALPHA_CROP_PADDING=6 像素后再裁。
    """
    a = np.asarray(img.getchannel("A"))
    mask = a > ALPHA_OPAQUE_THRESHOLD
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any() or not cols.any():
        return None
    img_h, img_w = a.shape
    top, bot = np.where(rows)[0][[0, -1]]
    left, right = np.where(cols)[0][[0, -1]]
    left = max(0, int(left) - ALPHA_CROP_PADDING)
    top = max(0, int(top) - ALPHA_CROP_PADDING)
    right = min(img_w - 1, int(right) + ALPHA_CROP_PADDING)
    bot = min(img_h - 1, int(bot) + ALPHA_CROP_PADDING)
    return (left, top, right - left + 1, bot - top + 1)


def plan_foreground_geometry(bounds: tuple[int, int, int, int] | None) -> dict | None:
    """由（并集）bbox 算出一套固定的 crop / resize / paste 参数。"""
    if bounds is None:
        return None
    left, top, bw, bh = bounds
    avail_w = max(1, AVATAR_STD_SIZE - FOREGROUND_SIDE_PADDING * 2)
    avail_h = max(1, AVATAR_STD_SIZE - FOREGROUND_TOP_PADDING - FOREGROUND_BOTTOM_PADDING)
    scale = min(avail_w / max(bw, 1), avail_h / max(bh, 1), 1.0)
    tw = max(1, int(bw * scale + 0.5))
    th = max(1, int(bh * scale + 0.5))
    return {
        "crop": (left, top, left + bw, top + bh),
        "size": (tw, th),
        "paste": (max(0, round((AVATAR_STD_SIZE - tw) / 2)),
                  max(0, AVATAR_STD_SIZE - th - FOREGROUND_BOTTOM_PADDING)),
        "bounds": [int(left), int(top), int(bw), int(bh)],
        "scale": round(scale, 6),
    }


def apply_foreground_geometry(img: Image.Image, geom: dict | None) -> Image.Image:
    """用固定几何把一帧重建到 512×512 全透明画布。"""
    if geom is None:
        return img
    cropped = img.crop(tuple(geom["crop"]))
    if cropped.size != tuple(geom["size"]):
        cropped = cropped.resize(tuple(geom["size"]), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (AVATAR_STD_SIZE, AVATAR_STD_SIZE), (0, 0, 0, 0))
    canvas.paste(cropped, tuple(geom["paste"]))
    return canvas


def plan_global_foreground_geometry(frame_paths: list[Path]) -> dict | None:
    """扫一遍所有 matte 帧，取不透明 bbox 的并集，算出全局几何。"""
    l = t = r = b = None
    for p in frame_paths:
        with Image.open(p) as im:
            bnd = extract_opaque_bounds(im.convert("RGBA"))
        if bnd is None:
            continue
        bl, bt, bw, bh = bnd
        br, bb = bl + bw, bt + bh
        l = bl if l is None else min(l, bl)
        t = bt if t is None else min(t, bt)
        r = br if r is None else max(r, br)
        b = bb if b is None else max(b, bb)
    if l is None:
        return None
    return plan_foreground_geometry((l, t, r - l, b - t))


def normalize_foreground_layer(img: Image.Image) -> Image.Image:
    """单图版 normalize（逐帧独立，完全对齐 app normalizeForegroundLayer）。

    1. extractOpaqueBounds — 裁掉 matte 周围透明空白（alpha<=14 当透明，外扩 6px）
    2. resizeInside(492×504) — 等比缩进可用区域（512-10*2, 512-8-0）
    3. 贴到全新的 512×512 全透明画布：水平居中 + 底部对齐

    ⚠️ 不要用它逐帧处理动画：每帧自己算 bbox 会导致位置/缩放逐帧漂移
    （前景"位置变来变去"）。动画走 plan_global_foreground_geometry()。
    本函数仅用于 normalize_mode=per-frame 的对照模式。
    """
    return apply_foreground_geometry(img, plan_foreground_geometry(extract_opaque_bounds(img)))


# --------- 背景生成（官方算法）---------

def build_official_background(src_first_frame: Image.Image,
                              matte_first_raw: Image.Image,
                              bg_side: int = DEFAULT_BG_SIDE) -> Image.Image:
    """对齐官方 createApproximateBackgroundLayer（separateRoleAvatar.ts L346）。

    参数逐项对应 app 的 createApproximateBackgroundLayer(source, foreground)：
      src_first_frame  ← normalizedInput：512 垫边的**原始首帧**（含完整场景）
      matte_first_raw  ← foregroundRaw：**未 normalize** 的 raw matte，只取 alpha

    ⚠️ 这两个参数都不能传 normalize 后的 matte。normalize 会把主体裁出来贴到全新
    透明画布上，画布其余部分 RGB 是纯黑 —— 背景因此丢掉整个场景，只剩「黑边 + 一
    个人」；再经第 4 步 cover 到 768（512→768 即 1.5× 放大 + 居中裁切），那个人被
    放大成一个巨大的模糊人影，和前景层里正常大小的清晰主体并排出现 = 肉眼可见的
    「双影」。本模块把 normalize 结果单独写到 _tmp_frames/norm/，matte/ 始终是 raw。

    1. 源帧 RGB 做 blur(12) + 亮度 1.01 + 饱和度 0.94
    2. raw matte 的 alpha 通道 blur(10) 作为人物 mask
    3. 仅人物区域叠加模糊版（"融"进背景）
    4. cover centre 到 bg_side × bg_side（fillOpaqueCanvas）
    """
    fg_rgb = src_first_frame.convert("RGB")
    w, h = fg_rgb.size  # 512×512

    # 1. 模糊底图
    blurred = fg_rgb.filter(ImageFilter.GaussianBlur(12))
    blurred = ImageEnhance.Brightness(blurred).enhance(1.01)
    blurred = ImageEnhance.Color(blurred).enhance(0.94)

    # 2. 人物 mask（raw matte alpha → blur 10，再 fill 到源图尺寸，对齐 sharp fit:fill）
    subject_mask = matte_first_raw.getchannel("A").filter(ImageFilter.GaussianBlur(10))
    if subject_mask.size != (w, h):
        subject_mask = subject_mask.resize((w, h), Image.Resampling.LANCZOS)

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


# ============================================================================
# 任务上下文
# ============================================================================

class WebpTask:
    """一个角色一次转换的全部路径与配置。

    分步命令之间不传状态，全靠 output_path 下的固定目录复用：
      {output_path}/_tmp_frames/src    抽帧结果（512 垫边原始帧）
      {output_path}/_tmp_frames/matte  抠图结果（**raw**，永不原地改写）
      {output_path}/_tmp_frames/norm   normalize 后的帧（编码 webp 的输入）
      {output_path}/_tmp_frames/_state.json  跨步骤统计（帧数/抠图耗时/几何）
    """

    def __init__(self, task: dict, cfg: dict, ffmpeg: str):
        self.task = task
        self.cfg = cfg
        self.ffmpeg = ffmpeg

        self.input_video: Path = task["input_video"]
        self.out_dir: Path = task["output_path"]
        self.normalize_mode: str = task["normalize_mode"]

        self.video_mp4 = self.out_dir / "video.mp4"
        self.first_frame_png = self.out_dir / "firstFrame.png"
        self.background_png = self.out_dir / "background.png"
        self.foreground_webp = self.out_dir / "foreground.webp"
        self.webp_json = self.out_dir / "webp.json"

        # 固定目录名（不带 pid/时间戳）：分步命令必须能复用上一步的抽帧结果
        self.tmp_root = self.out_dir / "_tmp_frames"
        self.src_dir = self.tmp_root / "src"
        self.matte_dir = self.tmp_root / "matte"
        self.norm_dir = self.tmp_root / "norm"
        self.state_path = self.tmp_root / "_state.json"

    # ---- 模型（严格按配置文件，代码内不换模型）----

    @property
    def model(self) -> str:
        return str(self.cfg["model"])

    @property
    def use_birefnet_rvm(self) -> bool:
        return self.model == "birefnet_rvm"

    @property
    def use_rembg(self) -> bool:
        """modnet 走 onnxruntime 直调；birefnet_rvm 走独立 worker；其余全走 rembg。"""
        return self.model not in ("modnet", "birefnet_rvm")

    def resolve_model_path(self) -> Path:
        cache = Path(self.cfg["model_cache"])
        if self.model == "modnet":
            return cache / DEFAULT_MODNET_MODEL.name
        if self.use_birefnet_rvm:
            return cache / DEFAULT_RVM_PTH.name
        # rembg 系（birefnet-portrait / u2net / u2netp / isnet-general-use）
        return cache / f"{self.model}.onnx"

    def check_matting_deps(self) -> Path:
        """校验抠图依赖齐备，返回模型文件路径。缺依赖直接报错，不降级换模型。"""
        model_path = self.resolve_model_path()
        if not model_path.exists():
            raise WebpError(
                f"配置指定的模型不存在: {model_path}\n"
                f"（config={self.cfg.get('config_path')} 中 model={self.model}）\n"
                "请把对应模型放进 model_cache 目录。不允许代码里改模型。"
            )
        if (self.use_rembg or self.use_birefnet_rvm) and not DEFAULT_PYTHON_BIREFNET.exists():
            raise WebpError(f"抠图用的 python 不存在: {DEFAULT_PYTHON_BIREFNET}")
        return model_path

    # ---- 帧 ----

    def src_frames(self) -> list[Path]:
        return sorted(self.src_dir.glob("frame_*.png"))

    def matte_frames(self) -> list[Path]:
        return sorted(self.matte_dir.glob("frame_*.png"))

    def require_frames(self, step: str) -> tuple[list[Path], list[Path]]:
        src = self.src_frames()
        matte = self.matte_frames()
        if not src or not matte:
            raise WebpError(f"{step} 需要先跑 --tmp_frames：{self.tmp_root} 下缺 src/ 或 matte/ 帧")
        return src, matte

    # ---- 跨步骤状态 ----

    def read_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def write_state(self, **patch) -> dict:
        state = self.read_state()
        state.update(patch)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return state


# ============================================================================
# 步骤
# ============================================================================

def step_video(t: WebpTask) -> dict:
    """1. input_video → {output_path}/video.mp4（原样复制，不重编码）。"""
    t.out_dir.mkdir(parents=True, exist_ok=True)
    if t.input_video == t.video_mp4:
        log(ok=True, phase="video_done", skipped="input_video 就是 video.mp4", path=str(t.video_mp4))
        return {"video": str(t.video_mp4)}
    for attempt in range(3):  # Windows 句柄延迟偶发锁文件
        try:
            shutil.copy2(t.input_video, t.video_mp4)
            break
        except PermissionError:
            if attempt == 2:
                raise
            time.sleep(1.5)
    log(ok=True, phase="video_done", path=str(t.video_mp4))
    return {"video": str(t.video_mp4)}


def step_tmp_frames(t: WebpTask) -> dict:
    """2. 抽帧 → _tmp_frames/src，逐帧抠图 → _tmp_frames/matte（raw）。"""
    model_path = t.check_matting_deps()
    fps = int(t.cfg["fps"])
    gif_side = int(t.cfg["gif_side"])
    max_seconds = int(t.cfg["max_seconds"])
    concurrency = int(t.cfg["concurrency"])

    t.src_dir.mkdir(parents=True, exist_ok=True)
    t.matte_dir.mkdir(parents=True, exist_ok=True)
    t.norm_dir.mkdir(parents=True, exist_ok=True)
    # 重跑必须先清旧帧：新一轮帧数变少时，尾部旧帧会残留并被一起编码进 webp
    for old in [*t.src_frames(), *t.matte_frames(), *sorted(t.norm_dir.glob("frame_*.png"))]:
        old.unlink(missing_ok=True)

    # 关键：decrease + pad 保持原比例（竖版视频用 increase 会砍头/砍脚）
    crop_animated = (
        f"fps={fps},"
        f"scale={gif_side}:{gif_side}:"
        f"force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={gif_side}:{gif_side}:(ow-iw)/2:(oh-ih)/2:color=0x00000000,"
        f"format=rgba"
    )
    run_ffmpeg(t.ffmpeg, [
        "-ss", "0", "-t", str(max_seconds),
        "-i", str(t.input_video),
        "-vf", crop_animated,
        str(t.src_dir / "frame_%04d.png"),
    ])

    src_frames = t.src_frames()
    if not src_frames:
        raise WebpError(f"抽帧失败，源目录为空: {t.src_dir}")
    log(ok=True, phase="frames_extracted", frame_count=len(src_frames))

    t0 = time.time()
    if t.use_birefnet_rvm:
        run_birefnet_rvm(t)
    else:
        model_dir = Path(t.cfg["model_cache"])
        jobs = [
            (i + 1, src, t.matte_dir, DEFAULT_PYTHON_BIREFNET, model_path,
             t.use_rembg, t.model, model_dir)
            for i, src in enumerate(src_frames)
        ]
        completed = 0
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = [ex.submit(matte_frame_wrapper, job) for job in jobs]
            for future in as_completed(futures):
                idx, ok, err = future.result()
                completed += 1
                if not ok:
                    raise WebpError(f"帧 {idx} 抠图失败: {err}")
                if completed % 5 == 0 or completed == len(src_frames):
                    log(ok=True, phase="matting", done=completed, total=len(src_frames),
                        elapsed_s=round(time.time() - t0, 2))
    matting_seconds = round(time.time() - t0, 2)

    matte_frames = t.matte_frames()
    if len(matte_frames) != len(src_frames):
        raise WebpError(f"抠图帧数不一致：src={len(src_frames)} matte={len(matte_frames)}")

    t.write_state(frames=len(src_frames), mattingSeconds=matting_seconds,
                  model=t.model, fps=fps, gifSide=gif_side, concurrency=concurrency)
    log(ok=True, phase="matting_done", total=len(src_frames),
        elapsed_s=matting_seconds, engine=t.model)
    return {"frames": len(src_frames), "mattingSeconds": matting_seconds, "tmpDir": str(t.tmp_root)}


def run_birefnet_rvm(t: WebpTask) -> None:
    """birefnet_rvm：首帧 BiRefNet 精抠 + RVM recurrent 传播 + EMA 平滑（独立 worker）。"""
    worker = next((p for p in RVM_WORKER_CANDIDATES if p.exists()), None)
    if worker is None:
        raise WebpError(
            "配置 model=birefnet_rvm，但 worker 脚本未找到。候选路径:\n  "
            + "\n  ".join(str(p) for p in RVM_WORKER_CANDIDATES)
        )
    proc = subprocess.run(
        [str(DEFAULT_PYTHON_BIREFNET), str(worker), str(t.src_dir), str(t.matte_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    for line in (proc.stderr or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            print(line, file=sys.stderr, flush=True)
    if proc.returncode != 0:
        raise WebpError(f"birefnet_rvm worker 失败: {(proc.stderr or '')[-1200:]}")


def step_background(t: WebpTask) -> dict:
    """3. src 首帧（RGB）+ raw matte 首帧（alpha）→ background.png。

    必须在 --foreground.webp 之前跑（或至少不依赖它）：background 要的是 raw matte。
    本模块 normalize 写到 norm/，matte/ 永远是 raw，所以两步先后可任意重跑。
    """
    src_frames, matte_frames = t.require_frames("--background")
    matte_first = t.matte_dir / "frame_0001.png"
    if not matte_first.exists():
        matte_first = matte_frames[0]
    bg_start = time.time()
    with Image.open(src_frames[0]) as si, Image.open(matte_first) as mi:
        bg = build_official_background(si.convert("RGBA"), mi.convert("RGBA"), int(t.cfg["bg_side"]))
    t.out_dir.mkdir(parents=True, exist_ok=True)
    bg.save(t.background_png, format="PNG")
    log(ok=True, phase="background_done", elapsed_s=round(time.time() - bg_start, 2),
        path=str(t.background_png))
    return {"background": str(t.background_png)}


def step_first_frame(t: WebpTask) -> dict:
    """4. input_video 第 0 秒 → firstFrame.png（原始分辨率，静态占位图）。"""
    t.out_dir.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(t.ffmpeg, ["-ss", "0", "-i", str(t.input_video), "-vframes", "1",
                          str(t.first_frame_png)])
    log(ok=True, phase="first_frame_done", path=str(t.first_frame_png))
    return {"firstFrame": str(t.first_frame_png)}


def step_foreground(t: WebpTask) -> dict:
    """5. raw matte → 统一几何 normalize 到 norm/ → libwebp_anim 编码 foreground.webp。"""
    assert_webp_anim_encoder(t.ffmpeg)
    _, matte_frames = t.require_frames("--foreground.webp")

    geom = None
    if t.normalize_mode == "global":
        geom = plan_global_foreground_geometry(matte_frames)
        log(ok=True, phase="geometry", mode="global",
            bounds=(geom or {}).get("bounds"), scale=(geom or {}).get("scale"),
            size=list((geom or {}).get("size") or []),
            paste=list((geom or {}).get("paste") or []))
    else:
        log(ok=True, phase="geometry", mode="per-frame")

    t.norm_dir.mkdir(parents=True, exist_ok=True)
    for old in sorted(t.norm_dir.glob("frame_*.png")):
        old.unlink(missing_ok=True)
    for mf in matte_frames:
        with Image.open(mf) as im:
            img = im.convert("RGBA")
        out = apply_foreground_geometry(img, geom) if t.normalize_mode == "global" \
            else normalize_foreground_layer(img)
        out.save(t.norm_dir / mf.name, format="PNG", optimize=False)
    log(ok=True, phase="normalize_done", mode=t.normalize_mode, frames=len(matte_frames))

    # 参数与 app renderSemanticAvatarAssets 逐项一致（不加 -preset）
    t.out_dir.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(t.ffmpeg, [
        "-framerate", str(int(t.cfg["fps"])),
        "-i", str(t.norm_dir / "frame_%04d.png"),
        "-c:v", "libwebp_anim",
        "-lossless", "1",
        "-quality", "90",
        "-compression_level", "4",
        "-loop", "0",
        "-an",
        "-vsync", "0",
        str(t.foreground_webp),
    ])
    patched = patch_anmf_disposal_background(t.foreground_webp)
    t.write_state(normalizeMode=t.normalize_mode, foregroundGeometry=geom,
                  frames=len(matte_frames))
    log(ok=True, phase="foreground_done", path=str(t.foreground_webp),
        size_bytes=t.foreground_webp.stat().st_size, disposalPatched=patched)
    return {"foreground": str(t.foreground_webp), "foregroundGeometry": geom}


def step_webp_json(t: WebpTask) -> dict:
    """6. 汇总以上产物 → webp.json。"""
    missing = [p.name for p in (t.video_mp4, t.first_frame_png, t.background_png, t.foreground_webp)
               if not p.exists()]
    if missing:
        raise WebpError(f"--webp.json 缺少前置产物 {missing}，请先跑对应步骤: {t.out_dir}")

    state = t.read_state()
    result = {
        "ok": True,
        "rolename": t.task["rolename"],
        "story": t.task["story"],
        "foreground": str(t.foreground_webp),
        "background": str(t.background_png),
        "firstFrame": str(t.first_frame_png),
        "video": str(t.video_mp4),
        "durationMs": get_video_duration_ms(t.ffmpeg, t.input_video),
        "frames": state.get("frames", len(t.matte_frames())),
        "gifSide": int(t.cfg["gif_side"]),
        "bgSide": int(t.cfg["bg_side"]),
        "fps": int(t.cfg["fps"]),
        "concurrency": int(t.cfg["concurrency"]),
        "model": t.model,
        "modelClass": "inanimate" if t.task["type"] == "inanimate" else "portrait",
        "type": t.task["type"],
        "normalizeMode": state.get("normalizeMode", t.normalize_mode),
        "foregroundGeometry": state.get("foregroundGeometry"),
        "mattingSeconds": state.get("mattingSeconds"),
        "tmpDir": str(t.tmp_root),
    }
    t.webp_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    log(ok=True, phase="webp_json_done", path=str(t.webp_json))
    return result


STEP_FUNCS = {
    "video": step_video,
    "tmp_frames": step_tmp_frames,
    "background": step_background,
    "firstFrame": step_first_frame,
    "foreground": step_foreground,
    "webp_json": step_webp_json,
}


def remove_tree(path: Path) -> None:
    """删目录，失败只告警不抛。

    不能只调一次 ignore_errors=True：Windows 下 rembg 子进程/索引器可能瞬时占着
    句柄，一次删不掉又被静默吞掉，临时帧就残留在产物目录里。
    """
    for attempt in range(4):
        shutil.rmtree(path, ignore_errors=True)
        if not path.exists():
            return
        time.sleep(0.5 * (attempt + 1))
    left = sum(1 for _ in path.rglob("*"))
    log(ok=True, warn=f"临时目录清理失败（残留 {left} 项），可手动删除: {path}")


# ============================================================================
# 入口
# ============================================================================

def webp_op(config: str | Path, path_json: str | Path, step: str = "",
            type_flag: str = "", keep_tmp: bool = True, ffmpeg: str = "") -> dict:
    """webp操作入口（供 cli 调用）

    config     配置文件路径，如 .workbuddy/config/vedio_to_webp.yml
    path_json  生图 json 入参路径
    step       "" → 跑完整流程；否则为 FULL_PIPELINE 中的单个步骤（支持 STEP_ALIASES
               里的 --video.mp4 / --foreground.webp / --webp.json 等写法）
    type_flag  "living" / "inanimate"，覆盖 path_json 里的 type
    keep_tmp   完整流程结束后是否保留 _tmp_frames（默认保留，便于分步重跑与复查）
    """
    raw_step = str(step or "").strip()
    norm_step = STEP_ALIASES.get(raw_step, STEP_ALIASES.get(raw_step.lower(), raw_step))
    if norm_step in ("living", "inanimate"):  # 兼容把类型当步骤传进来
        type_flag = type_flag or norm_step
        norm_step = ""
    if norm_step and norm_step not in STEP_FUNCS:
        raise WebpError(f"未知步骤: {step!r}，可选: {sorted(STEP_ALIASES)}")

    task = load_task_json(path_json)
    if type_flag:
        tf = str(type_flag).strip().lower()
        if tf not in ("living", "inanimate"):
            raise WebpError(f"type 只能是 living / inanimate，当前: {type_flag!r}")
        task["type"] = tf

    model_class = "inanimate" if task["type"] == "inanimate" else "portrait"
    cfg = load_webp_config(config, model_class)
    t = WebpTask(task, cfg, discover_ffmpeg(ffmpeg))

    steps = [norm_step] if norm_step else list(FULL_PIPELINE)
    log(ok=True, phase="start", rolename=task["rolename"], story=task["story"],
        type=task["type"], steps=steps, model=cfg["model"], fps=cfg["fps"],
        max_seconds=cfg["max_seconds"], gif_side=cfg["gif_side"],
        concurrency=cfg["concurrency"], normalize_mode=task["normalize_mode"],
        input_video=str(task["input_video"]), output_path=str(task["output_path"]),
        config=str(cfg["config_path"]), ffmpeg=t.ffmpeg)

    result: dict = {"ok": True}
    for s in steps:
        result.update(STEP_FUNCS[s](t))

    if not keep_tmp and not norm_step:
        remove_tree(t.tmp_root)
    else:
        log(ok=True, note=f"临时帧目录保留: {t.tmp_root}")

    print(json.dumps(result, ensure_ascii=False))
    return result


def add_webp_arguments(parser) -> None:
    """给 `webp` 子命令挂参数（cli.py 复用，避免选项名两处不一致）。"""
    g_type = parser.add_mutually_exclusive_group()
    g_type.add_argument("--living", dest="type_flag", action="store_const", const="living",
                        help="生物立绘：读 yml 的 model + *_MODNet/*_BIREFNET 配置块")
    g_type.add_argument("--inanimate", dest="type_flag", action="store_const", const="inanimate",
                        help="非生物：读 yml 的 model_inanimate + *_INANIMATE 配置块")

    g_step = parser.add_mutually_exclusive_group()
    for flag, const, helptext in (
        ("--video.mp4", "video", "只跑第 1 步：复制 video.mp4"),
        ("--tmp_frames", "tmp_frames", "只跑第 2 步：抽帧 + 逐帧抠图到 _tmp_frames"),
        ("--background", "background", "只跑第 3 步：生成 background.png"),
        ("--firstFrame", "firstFrame", "只跑第 4 步：生成 firstFrame.png"),
        ("--foreground.webp", "foreground", "只跑第 5 步：normalize + 合成 foreground.webp"),
        ("--webp.json", "webp_json", "只跑第 6 步：汇总 webp.json"),
    ):
        g_step.add_argument(flag, dest="step", action="store_const", const=const, help=helptext)

    parser.add_argument("config", help="配置文件，如 .workbuddy/config/vedio_to_webp.yml")
    parser.add_argument("path_json", help="生图 json 入参路径")
    parser.add_argument("--ffmpeg", default="", help="ffmpeg 路径（默认自动查找）")
    parser.add_argument("--no-keep-tmp", dest="keep_tmp", action="store_false",
                        help="完整流程结束后删除 _tmp_frames")
    parser.set_defaults(type_flag="", step="", keep_tmp=True)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m src.webp.webp",
        description="mp4 立绘 → foreground.webp / background.png / firstFrame.png / webp.json",
    )
    add_webp_arguments(parser)
    args = parser.parse_args(argv)
    try:
        webp_op(config=args.config, path_json=args.path_json, step=args.step or "",
                type_flag=args.type_flag or "", keep_tmp=args.keep_tmp, ffmpeg=args.ffmpeg)
    except WebpError as e:
        log(ok=False, error=str(e))
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())