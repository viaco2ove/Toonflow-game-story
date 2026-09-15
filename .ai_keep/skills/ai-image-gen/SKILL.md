---
name: ai-image-gen
description: AI 图像生成技能。支持四种生图通道：① ImageGen（ToolSearch → DeferExecuteTool，两步延迟调用）；② mmx CLI（MiniMax 生图，需 mmx_enable=true）；③ ToonFlow API（调用本地 Toonflow 服务器）；④ multimodal（大模型直出）。触发词：生图、生成图片、生成头像、生成封面、生成背景图、制作图片、做头像、做封面。
location: user
agent_created: true
tags:
  - image-generation
  - avatar
  - cover-image
  - toonflow
---
# 示例
可以参考[agners-ai.md](openai_gen/agners-ai.md) 对应提示词设计
- 图生图维持人物形象
/ai-image-gen [参考图]生成夜见的角色卡头像
- 图生图之风格参考，只是风格，不是维持人物形象
/ai-image-gen [参考图] 风格参考生成夜见的角色卡头像

# AI 图像生成技能（ai-image-gen）

## 通道总览

| 通道             | 优先级 | 依赖                                    | 适用场景                       |
|------------------|--------|-----------------------------------------|--------------------------------|
| **ImageGen**     | ⭐ 推荐 | ToolSearch 发现 → DeferExecuteTool 调用 | 文生图、角色头像、封面、背景图 |
| **multimodal**   | ⭐ 推荐 | 大模型直接支持                          | 简单场景快速出图               |
| **mmx CLI**      | 🔧 备用 | mmx CLI 已安装 + mmx_enable=true        | 批量生成、自动化脚本           |
| **ToonFlow API** | 🔧 备用 | 本地 ToonFlow 服务器运行                | ToonFlow 平台专用角色图        |
| **openai_gen**   | 🔧 备用 | openai api 协议                         | api                            |
---
特别注意不允许ai 自己换通道  ！！！！不允许自己换模型！！！
不允许违规。你可以发现问题，提出解决方案。但是不能自以为是！
## 配置文件
[ai_image_gen.yml](../../config/ai_image_gen.yml)
例子
```
ai_image_gen_default_fun: openai_gen
ai_image_openai_url: https://api.agnes-ai.cn/v1/images/generations
ai_image_openai_key: xxx
ai_image_openai_model: agnes-image-2.5-flash
```
ai_image_gen_default_fun 代表默认使用那个通道生成

## 角色卡头像规格
默认景别：中景
#### 1️⃣ 景别
| 景别 | 用途 | 画面范围 |
|------|------|----------|
| **大远景** | 宏大场景，建立世界观 | 人物渺小，环境主导 |
| **远景** | 环境关系，场景交代 | 人物全身，环境占70% |
| **全景** | 动作展示，空间关系 | 人物全身清晰可见 |
| **中景** | 肢体互动，日常叙事 | 膝盖以上 |
| **近景** | 表情神态，情绪传递 | 胸部以上 |
| **特写** | 情绪爆发，细节强调 | 面部或关键物件 |

## 故事封面和章节背景图片生成
故事封面:可以是生成背景图后再在上面叠加某个角色的头像
章节背景:推荐无具体人物或者有路人的场景。
示例 参考图的提示词
```
"参考图1的画面风格进行生成，生成章节背景图片，特点只有场景没有特点角色，当前章节背景环境为大罗宗山门，九千级石阶。云雾自谷底翻涌而上
```

### 使用示例
- /ai-image-gen 风格参考图 cover.png 生成 萧肿.md 的头像

### 工作原理
两步延迟调用：
1. **ToolSearch** — 让模型发现客户端可用的 `ImageGen` 工具
2. **DeferExecuteTool** — 用 `prompt` 参数调用工具生成图片

### 调用方式
当用户请求生成图片时，模型先执行一次 `ToolSearch`（如果有的话），然后用以下格式调用：

```
ToolSearch   # 发现 ImageGen 工具（仅首次需要，之后模型会记住）
DeferExecuteTool(tool_call_id=<ToolSearch返回的id>, tool_name=ImageGen, arguments={"prompt": "图片描述文本"})
```

### ImageGen 参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | ✅ | 图片描述文本（越详细越好） |

### 适用提示词结构
- **角色头像**：`{外貌描述}，{服装}，{表情}，{国风3D动画风格，单人全身}，{背景描述}`
- **故事封面**：`{场景描述}，{氛围}，{国风3D动画风格，高清，细节丰富}，{光线、色调}`
- **章节背景图**：`{场景描述}，{情绪基调}，{国风3D动画风格}，{视角/构图}`

### 示例：生成角色头像
```
ToolSearch
DeferExecuteTool(tool_call_id="xxx", tool_name=ImageGen, arguments={"prompt": "一位18岁的清冷校花少女，黑长直发垂至腰际，皮肤白皙，眉眼清冷，穿延城一中蓝白校服，单手拎着书包，气质出众。国风3D动画风格，单人全身。背景：延城一中黄昏的教学楼走廊，夕阳斜照，她身后墙壁上隐约有一道不属于任何人的、缓缓蠕动的阴影。"})
```

---

## 通道二：multimodal（推荐备选）

### 工作原理
由对接的大模型直接实现图片生成（无需额外工具调用）。直接输出图片。

### 使用方式
当用户请求生成图片且 ImageGen 不可用时，直接在对话中描述图片内容，模型可自行生成。

---

## 通道三：mmx CLI

### 前提条件
- 已安装 mmx CLI：`npm install -g @minimaxi/mmx`
- 已登录：`mmx auth`
- 配置文件中设置 `mmx_enable=true`（或 `~/.claude/mmx.conf`）

### 命令格式
```bash
mmx image "图片描述" --n <数量> --aspect-ratio <比例>
```

### 常用比例
| 比例 | 适用场景 |
|------|----------|
| 1:1 | 角色头像、头像 |
| 16:9 | 故事封面、宽屏背景 |
| 9:16 | 手机竖版封面 |
| 4:3 | 章节背景图 |

### 示例
```bash
# 生成 1 张角色头像
mmx image "一位18岁清冷校花少女，黑长直发，延城一中校服，国风3D动画风格，单人全身" --n 1 --aspect-ratio 1:1

# 生成 1 张故事封面
mmx image "延城一中校园，晨光下的教学楼，网球场边有异样的阴影，远景天际线上矗立着一座漆黑的巨塔，悬疑氛围，国风3D动画风格，高清" --n 1 --aspect-ratio 16:9
```

### 批量生成
```bash
# 批量生成多个角色的头像
for char in "张晚意" "林凡" "小满"; do
  mmx image "${char}的角色头像，国风3D动画风格，单人全身" --n 1 --aspect-ratio 1:1 --out "${char}.png"
done
```

---

## 通道四：ToonFlow API

### 前提条件
- 本地 ToonFlow 服务器运行中（默认端口 `60002`）
- 已配置正确的 `TOKEN`（在脚本中设置）

### API 端点
```
POST http://localhost:60002/game/generateImage
Authorization: Bearer <TOKEN>
Content-Type: application/json
```

### 请求体
```json
{
  "projectId": 1,
  "type": "role|cover|background",
  "prompt": "图片描述",
  "name": "图片名称",
  "base64List": [],
  "size": "2K"
}
```

### 使用场景
直接通过 curl 调用：
```bash
curl -X POST 'http://localhost:60002/game/generateImage' \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "projectId": 1,
    "type": "role",
    "prompt": "张晚意的角色头像，18岁清冷校花，国风3D动画风格",
    "name": "张晚意",
    "base64List": [],
    "size": "2K"
  }'
```

---

## 典型工作流（生成 AI 故事头像/封面）

### 步骤 1：确认图片需求
明确：角色头像 / 故事封面 / 章节封面 / 章节背景图

### 步骤 2：构造提示词
从对应 `.md` 文件中提取 `头像(ai生图形象描述)` 或 `章节背景图` 的提示词文本

### 步骤 3：选择通道生成
优先 ImageGen → 其次 multimodal → 备选 mmx CLI

### 步骤 4：保存到正确目录
| 类型 | 目标目录 |
|------|----------|
| 角色头像 | `ai_story/android_sj/<故事名>/avatars/<角色名>.png` |
| 故事封面 | `ai_story/android_sj/<故事名>/image/<故事名>/<故事名>_cover.jpg` |
| 章节封面 | `ai_story/android_sj/<故事名>/image/<故事名>/chapter_<N>_cover.jpg` |
| 章节背景图 | `ai_story/android_sj/<故事名>/image/<故事名>/chapter_<N>_background.jpg` |

### 步骤 5：更新角色文件中的头像引用
将 `- **头像**：（待生成）` 替换为 `![<角色名>.png](../avatars/<角色名>.png)`

---

## 子模块说明

| 目录 | 说明 |
|------|------|
| `AIModelHostGen/` | 文档：workbuddy / deepseek harness 调用生图的原理 |
| `imageGen/` | 文档：ImageGen 工具延迟调用方式 |
| `mmx/` | 文档：mmx CLI 命令行用法 |
| `toonFlow/` | 文档：ToonFlow 服务器 API 调用方式 |
| `multimodal/` | 文档：大模型直出生图 |


## 豆包app 提示词

- 参考图获取角色卡头像
```
中间那个独立出来做角色卡头像，竖屏，无边框
```

- 角色卡头像转5秒视频
```
做成5秒视频，要求镜头距离不能变化，只能人动，因为要做立绘。竖屏。
```

- 参考图获取角色卡头像
```
这个要做成角色卡头像，竖屏，无边框
```

- 画风参考
特点参考画风，就尽量减少画风的描述。只秒角色的形象和图片格式要求
```
[参考图]
参考图 1 这个画风，不要参考衣着和人脸生成角色卡头像，竖屏，无边框
新的角色要求：
前景：26 岁女性，深棕长卷发披肩，琥珀色眼瞳，唇角噙着妖冶的笑，穿暗红色皮衣皮裙，指甲涂暗红，手持一把收拢的折扇。半身像，
背景：北丘地下酒吧卡座，霓虹暗红，酒杯与雾气。

```