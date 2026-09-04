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

# AI 图像生成技能（ai-image-gen）

## 通道总览

| 通道 | 优先级 | 依赖 | 适用场景 |
|------|--------|------|----------|
| **ImageGen** | ⭐ 推荐 | ToolSearch 发现 → DeferExecuteTool 调用 | 文生图、角色头像、封面、背景图 |
| **multimodal** | ⭐ 推荐 | 大模型直接支持 | 简单场景快速出图 |
| **mmx CLI** | 🔧 备用 | mmx CLI 已安装 + mmx_enable=true | 批量生成、自动化脚本 |
| **ToonFlow API** | 🔧 备用 | 本地 ToonFlow 服务器运行 | ToonFlow 平台专用角色图 |

---

## 通道一：ImageGen（推荐）

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
