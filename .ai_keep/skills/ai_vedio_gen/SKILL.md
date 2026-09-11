---
name: ai_vedio_gen
description: >-
  AI 视频生成技能。基于 WorkBuddy 内置的 VideoGen 等工具，把文字描述或一张图片
  生成短视频（MP4）。支持文生视频、图生视频、首尾帧插值三种模式。
  触发词：生成视频、图生视频、视频生成、ai video、做一段视频、立绘动起来。
---



# AI 视频生成 (ai_vedio_gen)



## 通道总览

| 通道             | 优先级 | 依赖                             | 适用场景                                |
|------------------|--------|----------------------------------|-----------------------------------------|
| **VideoGen**     | ⭐ 推荐 | 当前ai 工具自己的能力            | WorkBuddy 等工具 内置的 VideoGen 等工具 |
| **multimodal**   | ⭐ 推荐 | 大模型直接支持                   | 简单场景快速出图                        |
| **mmx CLI**      | 🔧 备用 | mmx CLI 已安装 + mmx_enable=true | 批量生成、自动化脚本                    |
| **openai_gen**   | 🔧 备用 | openai api 协议                  | api                                     |

特别注意不允许ai 自己换通道  ！！！！不允许自己换模型！！！ 要根据配置文件来！！！！！！
不允许违规。你可以发现问题，提出解决方案。但是不能自以为是！
## 配置文件
[ai_vedio_gen.yml](../../config/ai_vedio_gen.yml)

例子
```
ai_vedio_gen_default_fun: openai_gen
ai_vedio_openai_url: https://api.agnes-ai.cn/v1/images/generations
ai_vedio_openai_key: xxx
ai_vedio_openai_model: agnes-image-2.5-flash
```
ai_vedio_gen_default_fun 代表默认使用那个通道生成
## 立绘相关视频要求

做人物立绘时，需要生成视频来展示立绘的动态效果。以下视频才符合立绘要求的视频标准：

> **⚠️ 最核心要求：镜头绝对不能动！镜头绝对不能动！镜头绝对不能动！**
>
> 人物立绘视频的本质是"静态画框里的人物微动"——画面中相机位置必须完全固定（无推拉摇移、无运镜），只有人物本身在动（呼吸起伏、发丝飘动、衣摆轻晃、眨眼、跳舞、表情变化 等）。任何镜头运动都会破坏立绘的展示效果，导致人物变形或画面偏移。
>
> 在写 prompt 时，必须明确标注 **镜头固定不动、固定机位、无运镜**，禁止出现镜头前推、镜头拉远、镜头环绕、运镜等任何运镜描述。

- **分辨率**：至少 720P（1280×720），推荐 1080P（1920×1080），保证人物细节清晰不模糊
- **比例**：竖屏 9:16 
- **帧率**：24fps 或 30fps，保证动作流畅不卡顿
- **时长**：5~10 秒短视频，适合做角色动态头像、立绘展示动效
- **画面内容**：以角色为中心，背景简洁不抢戏；人物构图完整（全身或半身），避免裁切掉头部或脚部
- **风格统一**：视频风格需与原立绘画风一致（二次元 / 写实 / 水彩等），避免风格跳脱
- **输出格式**：MP4（H.264 编码），便于直接嵌入游戏引擎或展示平台
- **镜头要求（最重要）**：相机必须完全固定，禁止任何推拉摇移跟甩等运镜操作。画面中只有人物在动（呼吸、眨眼、发丝飘动、衣摆轻晃、跳舞、表情变化 等），背景和画框保持绝对静止

其他不常用的比例，没有要求是vu使用： 3:4（适配角色全身/半身立绘展示），横屏 16:9 仅用于场景类背景图



## 何时用

- 想给角色立绘加微动效（呼吸 / 眨眼 / 衣摆飘动 / 轻微运镜）
- 凭文字描述直接生成一段动态画面
- 给章节背景图做动态预告
- 固定转场特效（拥抱 / 变身 / 万物归尘等）→ 走 `3D模型与视频特效` 技能的 video-fx，
  本技能不覆盖模板特效

## VideoGen
### workbuddy
查看 VideoGen/SKILL.workbuddy.md
ToolSearch 发现 → DeferExecuteTool 调用
把文字或图片变成短视频。底层走 **WorkBuddy 内置的 VideoGen 等工具**（不是外部
Connector，开箱即用，但调用消耗额外 credit）。

### minimax code
查看 VideoGen/SKILL.minimaxcode.md

## 角色视频生成

用于角色的动态头像（webp 文件）生成做准备。**所有生成的 mp4 必须写到缓存目录，不允许落到默认目录。**

### 输出目录（强制）

`{root}/.cache/character/{story}/{rolename}/`

- `{root}` =  项目根目录
- `{story}` = 故事名，如 `黑塔：从超忆症开始成神`
- `{rolename}` = 角色名，如 `先生`、`张晚意`

⚠️ **必须把完整路径通过 `output_dir` 参数传给 VideoGen，禁止依赖默认行为。**

### 角色视频默认参数

| 参数 | 值 |
|---|---|
| 格式 | MP4 |
| 时长 | 5s |
| 分辨率 | 720P |

### 生成方式

- VideoGen - WorkBuddy/minimax code 等工具内置多模态生成工具（调用消耗 credit）
- mmx mmx cli 生成视频
- doubao 豆包火山方舟 接口生成视频

### 配置文件

[ai_vedio_gen.yml](../../config/ai_vedio_gen.yml)

# 下面只是示例，调用的工具以技能使用者的要求和配置文件为准！

## 工具与参数(workbuddy-video-gen)

工具名：`VideoGen`（通过 `DeferExecuteTool` 调用，由 WorkBuddy 宿主提供）

| 参数 | 必填 | 说明                                                                   |
|---|---|------------------------------------------------------------------------|
| `prompt` | ✅ | 视频描述。具体写场景、动作、镜头运动、风格，越细越好                   |
| `image` | ❌ | 图生视频的输入图。本地绝对路径或 http(s) URL                           |
| `last_image` | ❌ | 尾帧图，做 image→last_image 帧间插值                                   |
| `seconds` | ❌ | 时长（秒），默认 5，建议 5–10                                          |
| `resolution` | ❌ | `720P`（默认）/ `1080P`，不要传其他值                                  |
| `output_dir` | ✅ | **必须传入**，完整路径如 `{root}/.cache/character/{story}/{rolename}/` |

## ⚠️ 必须告知用户的代价

- **Credit 消耗**：VideoGen 调用额外模型，**5 秒视频约 50–100 credits**。
  调用前必须明确告知用户这一消耗。
- **耗时**：生成 1–3 分钟，调用时设较长 timeout（建议 ≥ 240000ms）。
- **时长上限**：适合短视频，长剧情片需分镜 + 逐段生成 + ffmpeg 合成。

## 调用示例

### 图生视频（角色立绘微动效）

```json
{
  "toolName": "VideoGen",
  "params": {
    "prompt": "角色立绘轻微呼吸起伏，衣摆和发丝随风缓缓飘动，镜头完全固定不动，无运镜，人物构图不变，电影感柔光",
    "image": "/path/to/your/character.png",
    "seconds": 5,
    "resolution": "720P",
    "output_dir": "/path/to/cache/output/"
  }
}
```

### 文生视频

```json
{
  "toolName": "VideoGen",
  "params": {
    "prompt": "雨夜古城街道，灯笼摇曳，一个撑伞的身影缓缓走过青石板路，电影感，暖色调，镜头完全固定不动，无运镜",
    "seconds": 5,
    "resolution": "720P",
    "output_dir": "/path/to/cache/output/"
  }
}
```

### 首尾帧插值

```json
{
  "toolName": "VideoGen",
  "params": {
    "prompt": "从立绘自然过渡到消散粒子效果，镜头完全固定不动，无运镜",
    "image": "{root}/ai_story/android_sj/黑塔：从超忆症开始成神/avatars/先生.png",
    "last_image": "{root}/.cache/character/黑塔：从超忆症开始成神/先生/end_frame.png",
    "seconds": 5,
    "resolution": "720P",
    "output_dir": "{root}/.cache/character/黑塔：从超忆症开始成神/先生/"
  }
}
```

## 与本地合成的区别

| 方式 | 工具 | 适合 |
|---|---|---|
| AI 生成 | VideoGen | 凭空/图生动态画面，有 credit 成本 |
| 本地剪辑合成 | Python + moviepy/ffmpeg | 把已有图片+音频拼成视频、加字幕转场，零 credit |

章节预告片（背景图 + 旁白 voice.wav + 字幕）优先用 ffmpeg 合成，不烧 credit。

## 排查

| 症状 | 原因 | 解法 |
|---|---|---|
| credit 不足 | 额度耗尽 | 确认 WorkBuddy 账户额度 |
| 图生视频人物崩 | 原图构图复杂/多角色 | 简化 prompt，或先抠图再生成 |
| VideoGen 输出到 generated-videos 而非 .cache | 调用时漏了 output_dir 参数 | **必须**在每次 VideoGen 调用时显式传 `output_dir`，禁止留空 |
