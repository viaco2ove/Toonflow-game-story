---
name: convert-avatar-video-to-webp
description: >-
  把本地角色视频头像（.mp4）转成可用的 webp 动画头像 + png 背景。
  不走 Toonflow 服务端 /game/convertAvatarVideoToGif 接口，直接在本地
  串联 ffmpeg（抽帧/合成 webp）与 MODNet（onnxruntime 逐帧抠图），
  产出与 server 形态对齐的四个文件：foreground.webp、background.png、
  firstFrame.png、video.mp4。触发词：mp4 转 webp、本地抠图、modnet 抠图、
  本地视频转 webp 头像、不走接口转 webp。
---

# 本地视频转 webp 头像 (convert-avatar-video-to-webp) v4

## v4 修复重影根因：normalizeForegroundLayer 居中粘贴（2026-09-12）

**核心**：对齐 app `normalizeForegroundLayer` 的居中粘贴逻辑。

**根因**：v3 normalize 用"左/顶对齐"（`paste(resized, (10, 8))`），character 偏左→背景层沿边覆盖→重影。
app 用"水平居中 + 底部垂直对齐"（`left=(512-w)/2, top=512-h`）。

**修复**：
```python
# v3（左对齐）❌
canvas.paste(resized, (FOREGROUND_SIDE_PADDING, FOREGROUND_TOP_PADDING))

# v4（居中对齐）✅ 对齐 app normalizeForegroundLayer
left = max(0, round((AVATAR_STD_SIZE - w2) / 2))
top  = max(0, AVATAR_STD_SIZE - h2 - FOREGROUND_BOTTOM_PADDING)
canvas.paste(resized, (left, top))
```

**同时新增** `normalizeForegroundLayer` 等效函数（extractOpaqueBounds + resizeInside + 居中画布），在 colorkey 之前处理每一帧。

## v3 修复重影（2026-09-12）

| 修复 | 问题 | 方案 |
|------|------|------|
| **A. webp 无损编码** | v2 用 `lossless=0 + q=80` 有损压缩，alpha 边缘被压坏，背景色"漏"出形成重影 | 改为 `lossless=1 + quality=90 + compression_level=4`（对齐 app libwebp_anim） |
| **B. 背景用 512 垫边 matte 帧** | v2 对原始分辨率首帧重新抠图，mask 几何与抽帧管线不一致，导致背景人物区域偏移 | 直接复用 `matte_dir/frame_0001.png`（512×512，同管线产出） |
| **C. colorkey 软抠边** | 发丝/轮廓边缘残留的近黑像素（alpha 极低），无损压缩后"渗出"形成重影 | 对 matte 帧加 `colorkey=0x000000:0.08:0.05` 软透明化（对齐 app legacy 路径） |

### 重影根因分析

1. **WebP 编码参数（最直接）** — app 用无损，本技能用有损，半透明 alpha 被压掉
2. **背景图尺寸来源不一致** — matte 用 512 垫边帧，背景生成用原始分辨率重新抠图，几何错位
3. **边缘残留像素未处理** — 极低 alpha 的近黑像素在无损压缩后边界"渗出"

读取配置文件：
[vedio_to_webp.yml](../../config/vedio_to_webp.yml)
例如：
```
# 比较影响内存。建议内存不足的改为3. 不然可能会转换失败
VIDEO_TO_ANIMATION_MULTIPLIED_SPEED_MODNet: 6
# mp4 转动图动作帧的秒数，默认4
MAX_GIF_DURATION_SECONDS_MODNet: 5
# 每秒多少帧，默认10
GIF_FPS_MODNet: 15
FRAME_OUTPUT_SIDE_MODNet: 512

VIDEO_TO_ANIMATION_MULTIPLIED_SPEED_BIREFNE: 3
# mp4 转动图动作帧的秒数，默认4
MAX_GIF_DURATION_SECONDS_BIREFNET: 5
# 每秒多少帧，默认10
GIF_FPS_BIREFNET: 10
FRAME_OUTPUT_SIDE_BIREFNET: 512
# DATA_DIR: /data/toonflow or D:\Users\xxx\tools\Toonflow-game\toonflow-game-app\Toonflow-game or auto
DATA_DIR: auto
model_cache: "{DATA_DIR}\\avatar-matting\\birefnet\\model-cache"
# model: birefnet or modnet or rvm or birefnet_rvm(首帧 BiRefNet 精抠 + 后续帧 RVM 传播) or rvm
model: birefnet
# 非生物抠图模型：isnet-general-use/u2net/u2netp
model_inanimate: u2net
```

严格按照配置文件进行转换，不允许自己改模型。
不允许违规。你可以发现问题，提出解决方案。但是不能自以为是！

（非生物）inanimate 路径用 rembg + u2net 等模型 替代 portrait 模型，具体看model_inanimate 的参数配置
## 何时用

- 已有 `ai_vedio_gen` 生成的 mp4 视频头像，需要 webp 动图 + 背景 png
- 想避免服务端 `/game/convertAvatarVideoToGif` 的轮询/排队
- 批量把多个角色的 mp4 转成 webp（不写回服务器，纯本地产物）
- 服务端临时挂掉或想离线处理时

## 与现有技能的关系

| 技能 | 调用方式 | 产出 | 依赖 |
|---|---|---|---|
| `ai-story-webp-avatar-sync` | HTTP 接口，轮询 | webp 直写服务器 | Toonflow 服务端 + 排队 |
| **`convert-avatar-video-to-webp`** | **本地脚本** | **webp + png 落到 `.cache`** | **MODNet (onnxruntime) + ffmpeg** |

`ai-story-webp-avatar-sync` 走网络、产物写到服务器；本技能**完全本地**、
产物落到 `.cache/character/{story}/{rolename}/webp/` 目录。

## 流水线

```
.mp4 (输入)
   │
   ├──► ffmpeg -ss 0 -i input.mp4 -vframes 1  →  firstFrame.png
   │      │
   │      └──► ffmpeg -vf scale=768:768:...,crop=768:768  →  background.png
   │
   ├──► ffmpeg 抽帧：fps=10, scale=512:512, 最多前 4 秒  →  src_frames/frame_%04d.png
   │      │
   │      └──► MODNet (onnxruntime) 逐帧前景抠图（透明背景）  →  alpha_frames/frame_%04d.png
   │             │
   │             └──► ffmpeg libwebp 编码  →  foreground.webp
   │
   └──► cp →  video.mp4
```

> 与服务端 `convertAvatarVideoToGif.ts` 形态对齐：
> 服务端是 `colorkey=0x000000` 黑底键透明（假抠图），本技能用 **MODNet 真抠图**，
> 抗黑边、抗复杂背景，明显优于服务端版本。

## 输出文件（强制）

写到 `<out-dir>/`（默认 `{root}/.cache/character/{story}/{rolename}/webp/`）：

| 文件 | 说明 | 尺寸 | 格式 |
|---|---|---|---|
| `foreground.webp` | 透明背景的动画头像（角色前景，MODNet 抠图） | 512×512 | animated WebP |
| `background.png` | 首帧静态背景（720 边，正方形裁切，**含原角色**） | 768×768 | PNG |
| `firstFrame.png` | 原始首帧（不缩放） | 原分辨率 | PNG |
| `video.mp4` | 输入 mp4 副本 | 原分辨率 | MP4 |

`{root}` = 项目根目录，`{story}` = 故事名，`{rolename}` = 角色名。

## 默认参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--gif-side` | 512 | 前景 webp 边长（与 server 端 AVATAR_GIF_SIDE 一致） |
| `--bg-side` | 768 | 背景 png 边长（与 server 端 AVATAR_BG_SIDE 一致） |
| `--fps` | 10 | 抽帧率（与 server 端 GIF_FPS 一致） |
| `--max-seconds` | 4 | 取视频前 N 秒（与 server 端 MAX_GIF_DURATION_SECONDS 一致） |

## 模型选择（yml `model:`）

| 值 | 说明 | 适用 |
|---|---|---|
| `modnet` | onnxruntime 逐帧，快（~27s/40帧） | 通用兜底 |
| `birefnet` | rembg[birefnet-portrait] 逐帧，发丝级边缘 | 质量最优但**极慢（~12s/帧，40帧≈8min）** |
| `birefnet_rvm` | 首帧 BiRefNet + RVM 时序传播 + EMA | **推荐：质量接近 birefnet，36s 出 40 帧**（v3 默认） |

**⚠️ birefnet_rvm 的 dsr 坑（2026-09-08 定案）**：`--dsr` 原默认 0.25 是 RVM 官方 **1080p** 推荐值；512px 输入下缩小后特征图仅 128px，细节丢失导致 **RVM 把静态背景（桌椅）幻觉进 mask**（半透明像素 1.5%→5.2%，frame20 起肉眼可见残影）。**已改默认 dsr=0.75**（512×0.75=384px 特征图）：残影消失（半透回落 1.02%），抖动 0.00099 优于 MODNet（0.00152）。ema 0.85/0.95/1.0 影响很小。**口诀：dsr × 输入边长 ≥ 256px**。
质量排序（陈曦_6s.mp4 实测）：birefnet_rvm(dsr0.75) ≈ birefnet 逐帧 > modnet；速度：birefnet_rvm(36s) ≈ modnet(27s) >> birefnet(8min)。

### WebP 编码参数（v3 对齐 app）

| 参数 | v2（错误） | v3（正确，对齐 app） |
|---|---|---|
| `-lossless` | `0`（有损） | `1`（无损） |
| `-quality` | `80`（`q:v`） | `90` |
| `-compression_level` | `6` | `4` |

v2 有损编码是重影的直接原因之一。alpha 通道被压后半透明边缘"透"出背景色。

## ⚠️ U2NET_HOME（必须知道）

rembg 默认去 `~/.u2net/` 找 onnx，**找不到就会联网下载 928MB**（极慢、会挂死，残留 tmp 文件）。本地已有权重在：

```
…\avatar-matting\birefnet\model-cache\birefnet-portrait.onnx   (928MB)
```

`convert.py` 与 `_birefnet_rvm_worker.py` 已自动设置 `U2NET_HOME` 指向该目录。
手动跑 rembg 时务必：`export U2NET_HOME=<model-cache 目录>`，加载 ~10s，零下载。

## 依赖（必须）

| 依赖 | 路径 | 说明 |
|---|---|---|
| ffmpeg | 系统 PATH 或 `FFMPEG_PATH` 环境变量 | 抽帧 + libwebp 编码 |
| Python 3.13 | `D:\Users\viaco\tools\Toonflow-game\Toonflow-game-app\Toonflow-game\tools\avatar-matting\birefnet\venv\Scripts\python.exe` | 已装 onnxruntime/numpy/PIL |
| MODNet ONNX | `…\birefnet\model-cache\modnet_photographic_portrait_matting.onnx` | 24 MB，已下载 |

如不在默认位置，可用 `--python` / `--modnet-model` 显式指定。

## 工具与参数（convert.py）

| 参数 | 必填 | 说明 |
|---|---|---|
| `--mp4` | ✅ | 输入 mp4 路径（通常 `.cache/character/{story}/{rolename}/*.mp4`） |
| `--out-dir` | ✅ | 输出目录 |
| `--gif-side` | ❌ | 前景 webp 边长，默认 512 |
| `--bg-side` | ❌ | 背景 png 边长，默认 768 |
| `--fps` | ❌ | 抽帧率，默认 10 |
| `--max-seconds` | ❌ | 取前 N 秒，默认 4 |
| `--python` | ❌ | Python 解释器（默认自动定位 birefnet venv） |
| `--modnet-model` | ❌ | MODNet 模型路径（默认自动定位） |
| `--ffmpeg` | ❌ | ffmpeg 路径（默认从 `where ffmpeg` / 常见 Win 路径查找） |



**stdout 末尾**输出 JSON（方便脚本化调用）：

```json
{
  "ok": true,
  "foreground": "D:\\…\\webp\\foreground.webp",
  "background": "D:\\…\\webp\\background.png",
  "firstFrame": "D:\\…\\webp\\firstFrame.png",
  "video": "D:\\…\\webp\\video.mp4",
  "durationMs": 5042,
  "frames": 40
}
```

```
输出：{root}/.cache/character/{story}/{rolename}/webp
background.png
firstFrame.png
foreground.webp
video.mp4
webp.json
```

## 调用示例

### 单角色

```bash
python D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.workbuddy/skills/convert-avatar-video-to-webp/convert.py \
  --mp4   "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.cache/character/黑塔：从超忆症开始成神/林凡/林凡_6s.mp4" \
  --out-dir "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.cache/character/黑塔：从超忆症开始成神/林凡/webp"
```

### 批量（PowerShell）

```powershell
$root = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story"
$cache = "$root/.cache/character/黑塔：从超忆症开始成神"
$convert = "$root/.workbuddy/skills/convert-avatar-video-to-webp/convert.py"
Get-ChildItem $cache -Directory | ForEach-Object {
  $mp4 = Get-ChildItem $_.FullName -Filter *.mp4 | Select-Object -First 1
  if ($mp4) {
    $out = Join-Path $_.FullName 'webp'
    python $convert --mp4 $mp4.FullName --out-dir $out
  }
}
```

## 与 ai_vedio_gen 串联

```
avatars/<role>.png
   │  ai_vedio_gen  (VideoGen 图生视频，mp4 落 .cache)
   ▼
.cache/character/{story}/{role}/<role>_6s.mp4
   │  convert-avatar-video-to-webp  (本地 ffmpeg + MODNet)
   ▼
.cache/character/{story}/{role}/webp/
    ├─ foreground.webp
    ├─ background.png
    ├─ firstFrame.png
    └─ video.mp4
```

如果想同步到世界角色数据库，**仍然走** `ai-story-webp-avatar-sync`：
本技能只做**纯本地转换**，产物尚未上传服务器。

## 排查

| 症状 | 原因 | 解法 |
|---|---|---|
| `未找到 ffmpeg` | 系统无 ffmpeg | 安装 ffmpeg 并加 PATH，或 `--ffmpeg` 显式指定 |
| `onnxruntime not found` | 默认 venv 失效 | `--python` 指向带 onnxruntime 的环境 |
| `model not found` | 模型文件缺失 | 检查 `…\birefnet\model-cache\modnet_photographic_portrait_matting.onnx`；或重跑 `run_modnet.py --warmup` |
| webp 边缘发黑/有黑边 | MODNet 训练域外（动画 CG） | 一般不影响，必要时调 `--gif-side` 缩小；或改用 `birefnet-portrait`（见 run_birefnet.py） |
| 背景 png 上看不到角色 | 这是预期行为——背景是首帧，含原角色；webp 透明层叠在背景之上 | 客户端渲染层级问题，不是本技能 bug |
| 处理非常慢 | MODNet 逐帧 CPU 推理 | 24MB 模型单帧 0.5-2s（CPU），30 帧视频约 30-60s；如有 NVIDIA GPU 装 onnxruntime-gpu 可大幅加速 |

## 与服务端实现的差异

| 维度 | 服务端 `convertAvatarVideoToGif` | 本技能 |
|---|---|---|
| 抠图方式 | ffmpeg `colorkey=0x000000`（黑底键） | **MODNet 真实抠图**（onnxruntime） |
| 网络 | 必须 HTTP 提交+轮询 | 完全离线 |
| 队列 | 受服务端任务队列限制 | 本地串行 |
| 输出位置 | 写到 OSS 服务器 | 写到本地 `.cache` |
| 写回世界数据 | 是（`saveWorld`） | 否（仅生成文件） |

> 服务端的 colorkey 假抠图对"非纯黑背景"的视频失效（直接把背景当成透明）；
> 本技能的 MODNet 真抠图能处理任意背景，质量明显更好。


# 非生物的抠图
模型： isnet-general-use/u2net/u2netp
默认为u2net
对应配置文件的片段为
```
model_inanimate: u2netp
```
