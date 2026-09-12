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

# 本地视频转 webp 头像 (convert-avatar-video-to-webp)
## history
[重影.history.md](history/重影.history.md)

### 重影根因（v6 已定案，2026-09-13）

**结论：重影的唯一根因是 ffmpeg 的 webp 动画编码路径选错，不是抠图质量、不是 alpha 边缘。**

Animated WebP 每一帧（ANMF chunk）帧头有两位：

- `disposal method`：`0 = NONE`（保留上一帧画布）/ `1 = BACKGROUND`（先把该帧矩形清成背景/透明）
- `blending method`：`BLEND`（新帧 alpha 混合到画布）/ `NO_BLEND`（直接覆写）

规范默认是 `disposal=0 + BLEND`。这个组合下新帧里 alpha=0 的像素**不清画布，而是"露出上一帧"** → 这就是拖影的机械原理。对透明立绘（主体每帧都在动，让出的区域必须变透明）来说默认值是致命的。

| ffmpeg 路径 | 谁写 ANMF | 结果 |
|---|---|---|
| `-c:v libwebp`（或不写 `-c:v`，只给 `out.webp`） | `libavformat/webpenc.c` 自己手拼 ANMF，disposal **硬编码 0**，blend 走默认 BLEND | **必然重影** |
| `-c:v libwebp_anim` | 交给 libwebp 官方 `WebPAnimEncoder`，逐帧计算最小子矩形 + dispose/blend，保证解码结果 == 输入 | **不重影** |

这是 FFmpeg 挂了 7 年的 [ticket #7941](https://trac.ffmpeg.org/ticket/7941)，comment:19 直接定位到 `webpenc.c` 第 137 行 `avio_w8(s->pb, 0)`，补丁就是改成 `0x1`（dispose=BACKGROUND）。至今未合并、未暴露成选项。

**v3~v5 一直是 `-c:v libwebp`，所以无论怎么改 alpha 都治不好。v6 已改为 `libwebp_anim`。**

#### 实测证据（512×512 软边圆平移 12 帧，无损编码）

直接解析产物的 ANMF 帧头 + 统计每帧不透明像素（期望恒为 6036）：

```
=== libwebp（v5 旧） ===
  ANMF#01..12  512x512 @(0,0)  blend=BLEND     dispose=NONE
  实测 [6036, 8944, 11852, 14760, 17668, 20576, 23484, 26392, 29300, 32208, 35116, 38024]
  -> 重影帧: 2~12（逐帧线性累积，正是肉眼看到的拖影）

=== libwebp_anim（v6 新） ===
  ANMF#01..11   88x88  @(移动)  blend=NO_BLEND  dispose=BACKGROUND
  实测 [6036, 6036, 6036, 6036, 6036, 6036, 6036, 6036, 6036, 6036, 6036, 6036]
  -> 重影帧: 无
```

#### app 是怎么解决的

两条路径（`renderSemanticAvatarAssets` / `renderLegacyAvatarAssets`）都显式指定 `libwebp_anim`：

```
-c:v libwebp_anim  -lossless 1  -quality 90  -compression_level 4  -loop 0  -an  -vsync 0
```

三个要素按重要度排：

1. **`-c:v libwebp_anim`** ← 真正的根因修复。绕开 ffmpeg 自己拼 ANMF 的 bug，把 dispose/blend 决策权交回 libwebp。
2. **`-lossless 1`** ← 让帧间差分逐位精确。libwebp 在 lossless 下用 `IncreaseTransparency()`：把"与上一帧画布相同"的像素主动置成 alpha=0，靠 BLEND 从上一帧取回 —— 无损下是数学恒等；一旦 lossy，VP8 重建误差会让 blend 逐帧累积漂移，即使用了 libwebp_anim 也会有淡残影。所以它不是"编码质量"问题，而是**帧间差分的正确性前提**。
3. **每帧几何完全一致的全画布帧** ← `normalizeForegroundLayer` 把每帧重建到一张全新的 512×512 全透明画布（水平居中 + 底部对齐），`alpha<=14` 一律当透明裁边、外扩 6px。保证透明区 RGBA 逐帧位级一致，编码器算出的差分矩形就是真实运动区域。

#### 曾经的三个误判（v3~v5，均已在 v6 撤销）

| 版本 | 当时的"修复" | 为什么是误判 |
|---|---|---|
| v3 C | `colorkey=0x000000:0.08:0.05` 软抠边 | app 没有这一步；键掉近黑像素治的是单帧黑边，不是跨帧残留 |
| v4 | alpha 二值化（<128→0，>=128→255） | 把发丝/轮廓软边打成硬锯齿，是治不好病之后的错误代偿 |
| — | 有损/无损 | 方向对但定位错：坏的不是"半透明 alpha 边缘"，而是帧间差分的可逆性。alpha_quality 拉到 100，只要走 `-c:v libwebp` 照样重影 |

尺寸不一致 / 边缘残留产生的是**单帧内的空间缺陷**（错位、黑边光晕）；重影是**跨帧的时间缺陷**，两回事。

> **生物与非生物同时生效**：portrait（`birefnet` / `birefnet_rvm` / `modnet`）与 inanimate（`u2net` / `u2netp` / `isnet-general-use`）两条路径在 `convert.py` 里共用同一套 normalize（step 8）+ 编码（step 9），所以这一处修复对两者同时覆盖，无需分别处理。

> `convert.py` 启动时会执行 `assert_webp_anim_encoder()`：ffmpeg 不带 `libwebp_anim` **直接报错**，绝不静默回退到 `-c:v libwebp` 产出带拖影的 webp。


## 前景位置漂移根因（v7 已修）

重影治好后又出现的另一个症状：**“前景对象位置变来变去”**。这与重影无关，是 `normalize` 阶段的几何问题。

根因：app 的 `matteVideoFrame`（`convertAvatarVideoToGif.ts` L603）对**每一帧**单独调 `normalizeForegroundLayer`，每帧都按**自己的**不透明 bbox 重新 裁切 → 缩放 → 水平居中 + 底对齐，然后把 normalize 后的 buffer 写成 matte 帧（L721）。立绘微动视频里主体每帧会动几个像素，于是：

| bbox 变化 | 后果 |
|---|---|
| 宽高变 → scale 变 | 主体逐帧微缩放（呼吸感脉动） |
| 中心变 → 重新居中 | 真实位移被“拉回”，主体向反方向跳 |
| 底边变 → 底对齐 | 整体上下推 |

抠图 mask 本身逐帧不稳定时最致命：某帧丢了一块 → bbox 突变 → 整个主体被重新居中 → 疾飞几十像素。

**这是 app 自身的缺陷**，照抄会一起抄过来。v7 改为先求所有帧 bbox 的**并集**，算一次 crop/scale/paste，然后用**同一套几何**刷所有帧（包括背景首帧）：

- 帧间相对位置完整保留（真实微动还在），但不再整体漂移
- `background.png` 与 `foreground.webp` 用同一套几何 → 图层叠加不错位
- `libwebp_anim` 的差分矩形更小，体积也更小

实测（`收徒系统_立绘微动.mp4`，75 帧 / u2net / inanimate，`.cache/_ghost_probe/ab_v7.py`）：

```
=== per-frame（app 原行为）会引入的抖动 ===
  paste.x min/max = 40 181   spread = 141
  paste.y min/max = 21  49   spread = 28
  内容平移量 dx spread = 83   相邻帧 dx 最大跳变 = 74
  内容平移量 dy spread =  6   相邻帧 dy 最大跳变 =  5

=== global（v7 实际产物）===
  scale 固定 1.0，paste 固定 (40,18)，所有帧 dx=dy=0 → 无归一化抖动
```

相邻帧 74px 的水平突跳，就是肉眼可见的“位置变来变去”。

> `--normalize-mode` 默认 `global`。需要逐帧严格复现 app 行为时才传 `per-frame`（仅作对照，会抖）。
> 产物 `webp.json` 会写出 `normalizeMode` 与 `foregroundGeometry`（`bounds` / `scale` / `size` / `paste`）供核对。

> 残留问题（**不是** normalize 造成的）：rembg 逐帧独立推理，mask 本身会闪。上例中不透明像素数 min/max = 35502/71823（相差 2.02×），个别帧丢掉大半个对象。这是抠图模型的时序不稳定，portrait 路径可用 `birefnet_rvm`（RVM 递归传播 + EMA）缓解；inanimate 目前没有对应方案。


## 读取配置文件：
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
VIDEO_TO_ANIMATION_MULTIPLIED_SPEED_INANIMATE: 6
# mp4 转动图动作帧的秒数，默认4
MAX_GIF_DURATION_SECONDS_INANIMATE: 5
# 每秒多少帧，默认10
GIF_FPS_INANIMATE: 15
FRAME_OUTPUT_SIDE_INANIMATE: 512
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
   │             └──► ffmpeg -c:v libwebp_anim 编码  →  foreground.webp
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

### WebP 编码参数（v6 逐项对齐 app，不可改）

```
-framerate {fps} -i frame_%04d.png
-c:v libwebp_anim -lossless 1 -quality 90 -compression_level 4 -loop 0 -an -vsync 0
```

| 参数 | v2 | v3~v5 | v6（正确，对齐 app） |
|---|---|---|---|
| `-c:v` | 缺省（=libwebp） | `libwebp` ❌ | **`libwebp_anim`** ✅ 根因修复 |
| `-lossless` | `0`（有损） | `1` | `1` |
| `-quality` | `80`（`q:v`） | `90` | `90` |
| `-compression_level` | `6` | `4` | `4` |
| `-preset` | — | `picture` ❌ | **不加**（app 没有） |

## webp 合成的重影问题

只有一处修复：**编码器必须是 `libwebp_anim`**（详见上面"重影根因"）。
配合 `normalizeForegroundLayer`（每帧重建到统一的 512×512 全透明画布，居中 + 底对齐）
保证帧间几何一致，编码器才能算出正确的差分矩形。
**不做** alpha 二值化，**不做** colorkey 软抠边 —— app 都没有，加了只会破坏软边。


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
| ffmpeg | 系统 PATH 或 `FFMPEG_PATH` 环境变量 | 抽帧 + **`libwebp_anim`** 编码（必须 `--enable-libwebp` 构建；官方 win64-gpl-shared 已含） |
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
| `--model-class` | ❌ | `portrait`（默认，读 yml `model`）/ `inanimate`（读 yml `model_inanimate`） |
| `--normalize-mode` | ❌ | `global`（默认，v7：全局 bbox 并集，前景不漂移）/ `per-frame`（逐帧各算，等同 app，会抖） |
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
| `当前 ffmpeg 不带 libwebp_anim 编码器` | ffmpeg 未用 `--enable-libwebp` 构建 | 换官方 win64-gpl-shared 构建；**不要**改回 `-c:v libwebp`，那必然重影 |
| webp 有重影/拖影 | 编码器被改回 `-c:v libwebp` | 改回 `libwebp_anim`（见"重影根因"），并用 `.cache/_ghost_probe/probe4.py` 复测 |
| webp 边缘发黑/有黑边 | MODNet 训练域外（动画 CG） | 一般不影响，必要时调 `--gif-side` 缩小；或改用 `birefnet-portrait`（见 run_birefnet.py） |
| 背景 png 上看不到角色 | 这是预期行为——背景是首帧，含原角色；webp 透明层叠在背景之上 | 客户端渲染层级问题，不是本技能 bug |
| 前景对象位置变来变去 / 主体跳动 | 逐帧各自重新居中（`--normalize-mode per-frame`） | 用默认 `global`（见“前景位置漂移根因”），并用 `.cache/_ghost_probe/ab_v7.py` 复测 |
| 主体局部闪烁 / 某帧丢块 | 抠图模型逐帧独立推理，mask 时序不稳定 | portrait 改 `model: birefnet_rvm`；inanimate 暂无方案，可降 fps / 换 `isnet-general-use` 试 |
| 背景与前景错位 | 两者几何不同源 | v7 已保证 `background.png` 与所有前景帧共用同一套几何；核对 `webp.json.foregroundGeometry` |
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

非生物路径只替换抠图模型与并发/时长/FPS 配置块（`*_INANIMATE`），
**normalize（step 8）与 webp 编码（step 9）与生物路径完全共用**，
因此 `libwebp_anim` 的重影修复（v6）与全局几何修复（v7）对非生物同样生效，无需额外处理。

非生物已验证样本：`收徒系统_立绘微动.mp4` → 75 帧 / 15fps / u2net，ANMF 全部 `NO_BLEND`（无重影），`foregroundGeometry.scale=1.0` `paste=(40,18)`（无漂移）。

