---
name: ai_vedio_gen
description: >-
  AI 视频生成技能。基于 WorkBuddy 内置的 VideoGen 等工具，把文字描述或一张图片
  生成短视频（MP4）。支持文生视频、图生视频、首尾帧插值三种模式。
  触发词：生成视频、图生视频、视频生成、ai video、做一段视频、立绘动起来。
---



# AI 视频生成 (ai_vedio_gen)

把文字或图片变成短视频。底层走 **WorkBuddy 内置的 VideoGen 等工具**（不是外部
Connector，开箱即用，但调用消耗额外 credit）。

## 何时用

- 想给角色立绘加微动效（呼吸 / 眨眼 / 衣摆飘动 / 轻微运镜）
- 凭文字描述直接生成一段动态画面
- 给章节背景图做动态预告
- 固定转场特效（拥抱 / 变身 / 万物归尘等）→ 走 `3D模型与视频特效` 技能的 video-fx，
  本技能不覆盖模板特效

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

- VideoGen - WorkBuddy 内置多模态生成工具（调用消耗 credit）
- mmx mmx cli 生成视频
- doubao 豆包火山方舟 接口生成视频

### 配置文件

[ai_vedio_gen.yml](../../config/ai_vedio_gen.yml)

## 工具与参数

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
    "prompt": "角色立绘轻微呼吸起伏，衣摆和发丝随风缓缓飘动，镜头极缓慢前推，保持人物构图不变，电影感柔光",
    "image": "{root}/ai_story/android_sj/黑塔：从超忆症开始成神/avatars/先生.png",
    "seconds": 5,
    "resolution": "720P",
    "output_dir": "{root}/.cache/character/黑塔：从超忆症开始成神/先生/"
  }
}
```

### 文生视频

```json
{
  "toolName": "VideoGen",
  "params": {
    "prompt": "雨夜古城街道，灯笼摇曳，一个撑伞的身影缓缓走过青石板路，电影感，暖色调",
    "seconds": 5,
    "resolution": "720P",
    "output_dir": "{root}/.cache/character/黑塔：从超忆症开始成神/先生/"
  }
}
```

### 首尾帧插值

```json
{
  "toolName": "VideoGen",
  "params": {
    "prompt": "从立绘自然过渡到消散粒子效果",
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
