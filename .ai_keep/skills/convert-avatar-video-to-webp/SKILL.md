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
本地视频转 webp 头像 的cli 脚本
[webp.py](/src/webp/webp.py)

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
# model: birefnet/modnet/rvm/birefnet_rvm/rvm/SegmentCommonImage/u2net/u2net_modnet
# SegmentCommonImage 为阿里云的在线抠图模型
# birefnet_rvm(首帧 BiRefNet 精抠 + 后续帧 RVM 传播) 
# u2net_modnet:u2net 出粗 mask → trimap → MODNet 融合
# 质量： modnet < birefnet，其他的模型人像不稳定。modnet 是较差但稳定
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



# 重影根因分析
重影是合成webp 时导致的，上一帧的图像残留到了下一帧导致了图像拖影。

#### 不太重要的原因
1. **WebP 编码参数（最直接）** — app 用无损，本技能用有损，半透明 alpha 被压掉
2. **背景图尺寸来源不一致** — matte 用 512 垫边帧，背景生成用原始分辨率重新抠图，几何错位
3. **边缘残留像素未处理** — 极低 alpha 的近黑像素在无损压缩后边界"渗出"

#### 真正的原因和解决
Animated WebP 每一帧（ANMF chunk）有两个位：
disposal method：0 = NONE（保留上一帧画布）、1 = BACKGROUND（先把该帧矩形清成背景色/透明）
blending method：+b = BLEND（新帧 alpha 混合到画布上）、-b = NO_BLEND（直接覆写）
规范默认值是 disposal=0 + blend=BLEND。 这个组合下，新帧里 alpha=0 的像素不会清掉画布，而是"露出上一帧" → 这就是拖影/重影的机械原理。对透明立绘动画（主体每帧都在动，让出的区域必须变透明）来说，默认值是致命的。而 ffmpeg 有两条完全不同的 webp 动画输出路径：
路径	谁写 ANMF	结果
-c:v libwebp（或者干脆不写 -c:v，只给 out.webp）	libavformat/webpenc.c 自己手拼 ANMF，disposal 硬编码为 0，blend 走默认 BLEND	必然重影
-c:v libwebp_anim	交给 libwebp 官方 WebPAnimEncoder，由它逐帧计算子矩形 + dispose/blend，保证解码结果 == 输入	不重影
这是 FFmpeg 挂了 7 年的 ticket #7941，comment:19 直接定位到 webpenc.c 第 137 行 avio_w8(s->pb, 0)，补丁就是改成 0x1（dispose=BACKGROUND）。至今未合并、未暴露成选项。
app 是怎么解决的
两条路径都显式指定了 libwebp_anim，见 renderSemanticAvatarAssets 和 renderLegacyAvatarAssets：
-c:v libwebp_anim  -lossless 1  -quality 90  -compression_level 4  -loop 0  -an  -vsync 0
三个要素按重要度排：
-c:v libwebp_anim ← 真正的根因修复。绕开 ffmpeg 自己拼 ANMF 的 bug，把 dispose/blend 决策权交回 libwebp。
-lossless 1 ← 让上面那套帧间差分逐位精确。libwebp 在 lossless 下用 IncreaseTransparency()：把"与上一帧画布相同"的像素主动置成 alpha=0，靠 BLEND 从上一帧取回。这在无损下是数学恒等；一旦 lossy，VP8 重建误差会让 blend 逐帧累积漂移，即使用了 libwebp_anim 也会出现淡淡的残影。所以它不是"编码质量"问题，而是帧间差分的正确性前提。
每帧几何完全一致的全画布帧 ← normalizeForegroundLayer 把每帧都重建到一张全新的 512×512 全透明画布（background: {r:0,g:0,b:0,alpha:0}，水平居中 + 底部对齐），alpha<=14 一律当透明裁边。这保证透明区的 RGBA 逐帧位级一致，编码器算出的差分矩形就是真实运动区域，不会因为主体抖动/画布尺寸漂移而留下矩形外的旧像素。
你列的三条为什么是次要的
有损/无损：方向对了，但定位错了 —— 它坏的不是"半透明 alpha 边缘"，而是帧间差分的可逆性。就算你把 alpha_quality 调到 100，只要走了 -c:v libwebp 路径照样重影。
尺寸不一致 / 边缘残留：这些产生的是错位和黑边光晕，是单帧内的空间缺陷；重影是跨帧的时间缺陷，两回事。
