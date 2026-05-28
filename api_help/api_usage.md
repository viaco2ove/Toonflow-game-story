# Toonflow Game API 使用帮助文档

> 基于 toonflow-game-app 源码（src/routes/game/）整理
> 服务器地址：<ADDRESS_REDACTED>
> 认证 Token（admin）：见 `.env` 文件中的 `auth_token` 字段
> 文档更新时间：2026-05-28

---

## 快速导航

1. [认证方式](#认证方式)
2. [通用说明](#通用说明)
3. [世界管理 API](#世界管理-api)
4. [章节管理 API](#章节管理-api)
5. [任务管理 API](#任务管理-api)
6. [角色管理 API](#角色管理-api)
7. [会话/消息 API](#会话消息-api)
8. [Python 调用模板](#python-调用模板)
9. [curl 调用注意事项（Windows）](#curl-调用注意事项windows)
10. [已创建数据汇总](#已创建数据汇总)

---

## 认证方式

所有 `/game/*` 接口（除白名单外）需要 Token 认证。

**方式一：请求头（推荐）**

```
<SECRET_REDACTED> <token>
```

**方式二：Query 参数**

```
?<SECRET_REDACTED>
```

Token 用 JWT 格式，payload 里的 `id` 字段即 userId。
Token 有效期至 `1795462009`（Unix 秒，约 2026-11-24），过期后需重新登录获取。

**白名单（无需 Token）：**
- `/other/login`
- `/other/register`

---

## 通用说明

- 所有写入接口（POST）接受 `application/json`
- 读取接口（POST）也用 JSON body（不是 query 参数）
- 返回格式：`{ "code": 200, "data": {...}, "message": "..." }`
- `code=200` 为成功，非 200 为失败
- userId 从 Token 的 JWT payload 自动解析，**不可伪造**
- `settings` 字段：存入时是 JSON 字符串，`normalizeWorldSettings` 读取时自动 `JSON.parse`

---

## 世界管理 API

### 1. 创建/更新世界 — POST `/game/saveWorld`

> **关键**：`worldId` 为空或为 0 时创建新世界；有 `worldId` 且数据库存在时更新。

**请求体字段：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| worldId | number | 否 | 有则更新，无则创建 |
| projectId | number | **是** | 所属项目ID（需属于当前用户，否则 403） |
| name | string | **是** | 世界名称 |
| intro | string | 否 | 世界简介 |
| coverPath | string | 否 | 封面图路径（如 `/1/game/world/xxx.png`） |
| publishStatus | string | 否 | `draft` / `publishing` / `published` |
| settings | object/string | 否 | 世界设置（见下方结构） |
| playerRole | object | 否 | 玩家角色信息 |
| narratorRole | object | 否 | 旁白角色信息 |

**settings 结构：**

```json
{
  "roles": ["npc_xxx", "npc_yyy"],
  "narratorVoice": "混合（清朗温润）",
  "narratorVoiceMode": "text",
  "narratorVoicePresetId": "",
  "narratorVoiceReferenceAudioPath": "",
  "narratorVoiceReferenceAudioName": "",
  "narratorVoiceReferenceText": "",
  "narratorVoicePromptText": "",
  "narratorVoiceMixVoices": [],
  "globalBackground": "",
  "coverPath": "",
  "coverBgPath": "",
  "allowRoleView": true,
  "allowChatShare": true,
  "publishStatus": "draft",
  "chapterExtras": [
    {
      "chapterId": 52,
      "sort": 1,
      "openingRole": "旁白",
      "openingLine": "你本以为这只是一次普通的回乡探亲。",
      "background": "/1/game/scene/xxx.png",
      "music": "",
      "musicAutoPlay": true,
      "conditionVisible": true
    }
  ]
}
```

> **踩坑经验**：`chapterExtras` 的 `background` 字段在数据库里存的是 `backgroundPath`，前端用 `background` 字段，保存时需注意映射。

**playerRole / narratorRole 结构：**

```json
{
  "id": "player",
  "name": "用户",
  "roleType": "player",
  "description": "玩家角色描述",
  "attributes": {},
  "parameterCardJson": null
}
```

**返回示例：**

```json
{
  "code": 200,
  "data": {
    "id": 35,
    "projectId": 1,
    "name": "我的诡异表妹",
    "intro": "...",
    "settings": "{...}",
    "playerRole": "{...}",
    "narratorRole": "{...}",
    "createTime": 1779911634895,
    "updateTime": 1779913910542,
    "coverPath": "",
    "publishStatus": "draft",
    "coverBgPath": ""
  },
  "message": "更新世界观成功"
}
```

---

### 2. 获取世界 — POST `/game/getWorld`

**请求体：**
```json
{ "worldId": 35 }
```

---

### 3. 删除世界 — POST `/game/deleteWorld`

**请求体：**
```json
{ "worldId": 35 }
```

---

### 4. 列出世界 — POST `/game/listWorlds`

**请求体：** 空对象 `{}` 或 `{ "projectId": 1 }`

---

### 5. 复制世界 — POST `/game/copyWorld`

**请求体：**
```json
{
  "worldId": 35,
  "newName": "我的诡异表妹（副本）"
}
```

---

## 章节管理 API

### 1. 创建/更新章节 — POST `/game/saveChapter`

> **关键**：`chapterId` 为空或为 0 时创建新章节；有 `chapterId` 且存在时更新。

**请求体字段：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chapterId | number | 否 | 有则更新，无则创建 |
| worldId | number | **是** | 所属世界ID（必须先存在） |
| title | string | **是** | 章节标题 |
| content | string | 否 | 章节内容（特殊格式，见下方） |
| chapterKey | string | 否 | 章节Key（唯一标识） |
| backgroundPath | string | 否 | 背景图路径 |
| openingRole | string | 否 | 开场角色名（如 `旁白`） |
| openingText | string | 否 | 开场台词 |
| bgmPath | string | 否 | 背景音乐路径 |
| bgmAutoPlay | boolean | 否 | 音乐是否自动播放（默认 `true`） |
| showCompletionCondition | boolean | 否 | 是否显示完成条件 |
| entryCondition | object | 否 | 进入条件（JSON） |
| completionCondition | object | 否 | 完成条件（JSON） |
| runtimeOutline | object | 否 | 运行时大纲（通常由 AI 生成，保存时自动构建） |
| sort | number | 否 | 排序（越大越靠后，默认 0） |
| status | string | 否 | `draft` / `published` |

**content 格式说明：**

使用 `@角色名：` 标记对话角色， `\n` 换行：

```
@旁白：你走进了一间昏暗的房间。
@旁白：房间里有一张桌子，上面放着一封信。
@小七：表哥，你终于来了。
@旁白：她的笑容让你感到一阵寒意。
```

**completionCondition 格式：**

```json
{ "type": "user_input", "prompt": "用户输入了名称 性别，年龄" }
```

或

```json
{ "type": "user_choice", "expected": "跟小七去见校长" }
```

**返回示例：**

```json
{
  "code": 200,
  "data": {
    "id": 52,
    "worldId": 35,
    "title": "第1章：自由章节",
    "content": "...",
    "openingRole": "旁白",
    "openingText": "你本以为这只是一次普通的回乡探亲。",
    "bgmAutoPlay": true,
    "status": "draft",
    "sort": 0,
    "runtimeOutline": {
      "openingMessages": [...],
      "phases": [],
      "userNodes": [],
      "fixedEvents": [],
      "endingRules": {"success": [], "failure": [], "nextChapterId": null}
    }
  },
  "message": "更新章节成功"
}
```

---

### 2. 获取章节 — POST `/game/getChapter`

**请求体：**
```json
{ "chapterId": 52 }
```

---

### 3. 删除章节 — POST `/game/deleteChapter`

**请求体：**
```json
{ "chapterId": 52 }
```

---

### 4. 初始化章节 — POST `/game/initChapter`

**请求体：**
```json
{ "chapterId": 52, "worldId": 35 }
```

---

## 任务管理 API

### 1. 创建/更新任务 — POST `/game/saveTask`

> **关键**：`taskId` 为空或为 0 时创建新任务；有 `taskId` 且存在时更新。
> **踩坑经验**：`chapterId` 必须先有对应的章节记录，否则返回 `"chapterId 不存在"`。

**请求体字段：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| taskId | number | 否 | 有则更新，无则创建 |
| chapterId | number | **是** | 所属章节ID（必须先存在） |
| parentTaskId | number | 否 | 父任务ID（子任务） |
| title | string | **是** | 任务标题 |
| taskType | string | 否 | `main` / `side` / `hidden`（默认 `main`） |
| goalType | string | 否 | `dialogue`（默认）/ 其他 |
| successCondition | object | 否 | 成功条件（JSON） |
| failCondition | object | 否 | 失败条件（JSON） |
| rewardAction | object | 否 | 奖励动作（JSON） |
| sort | number | 否 | 排序（越大越靠后） |
| status | string | 否 | `todo` / `done` / `failed`（默认 `todo`） |

**successCondition / failCondition 格式：**

```json
{ "type": "user_choice", "expected": "跟小七去见校长" }
```

```json
{ "type": "user_input_keyword", "keywords": ["表妹", "小七"] }
```

```json
{ "type": "talk_to_npc", "npc": "李明" }
```

**rewardAction 格式：**

```json
{ "type": "give_item", "item": "小七的护身符" }
```

```json
{ "type": "gain_exp", "amount": 50 }
```

---

### 2. 获取任务 — POST `/game/getTask`

**请求体：**
```json
{ "taskId": 1 }
```

---

### 3. 获取任务 API 数据 — POST `/game/getTaskApi`

**说明**：获取任务在运行时的 API 格式数据（供游戏运行时使用）

**请求体：**
```json
{ "taskId": 1 }
```

---

## 角色管理 API

### 1. 导入世界角色 — POST `/game/importWorldRole`

> 从其他世界导入角色到当前世界（复制角色数据）

**请求体：**
```json
{
  "worldId": 35,
  "sourceWorldId": 30,
  "roleIds": ["npc_xxx", "npc_yyy"]
}
```

---

### 2. 列出可导入角色 — POST `/game/listImportableRoles`

**请求体：**
```json
{ "worldId": 35 }
```

---

### 3. 分隔角色头像 — POST `/game/separateRoleAvatar`

> 将角色的原始图片分隔为前景（头像）和背景

**请求体：**
```json
{
  "roleId": "npc_xxx",
  "imagePath": "/1/game/role/xxx_original.png"
}
```

---

## 会话/消息 API

### 1. 开始会话 — POST `/game/startSession`

**请求体：**

```json
{
  "worldId": 35,
  "chapterId": 52,
  "playerName": "玩家名称",
  "playerGender": "男",
  "playerAge": 20
}
```

---

### 2. 继续会话 — POST `/game/continueSession`

**请求体：**
```json
{ "sessionId": "session_xxx" }
```

---

### 3. 添加消息 — POST `/game/addMessage`

**请求体：**
```json
{
  "sessionId": "session_xxx",
  "role": "用户",
  "content": "我跟小七去见校长"
}
```

---

### 4. 获取消息 — POST `/game/getMessage`

**请求体：**
```json
{ "sessionId": "session_xxx", "limit": 50 }
```

---

### 5. 提交叙事回合 — POST `/game/commitNarrativeTurn`

> AI 处理后的叙事回合提交（通常由系统内部调用，非手动调用）

---

### 6. 列出会话 — POST `/game/listSession`

**请求体：**
```json
{ "worldId": 35 }
```

---

## Python 调用模板

> **推荐使用 Python 而非 curl（Windows 下 curl 多行 JSON 处理极其麻烦）**

### 基础模板

```python
import urllib.request, json

BASE_URL = "http://122.51.232.171:60002"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzc5OTEwMDA5LCJleHAiOjE3OTU0NjIwMDl9.FlDWRs9KmFo97rt9sob8emsQC5IXdVUZTlvC6wXCNL8"

def api_call(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": 500, "message": str(e)}

# 示例：获取世界
result = api_call("/game/getWorld", {"worldId": 35})
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 创建世界示例

```python
result = api_call("/game/saveWorld", {
    "projectId": 1,
    "name": "我的诡异表妹",
    "intro": "用户误入诡异世界，认错诡异小七为表妹",
    "publishStatus": "draft",
    "settings": {
        "roles": [],
        "narratorVoice": "混合（清朗温润）",
        "narratorVoiceMode": "text",
        "allowRoleView": True,
        "allowChatShare": True,
        "publishStatus": "draft",
        "chapterExtras": []
    },
    "playerRole": {
        "id": "player",
        "name": "用户",
        "roleType": "player",
        "description": "小七认错的表哥，技能：运气比较好"
    },
    "narratorRole": {
        "id": "narrator",
        "name": "旁白",
        "roleType": "narrator",
        "description": "负责环境推进、规则提示与节奏控制"
    }
})
```

### 批量创建任务示例

```python
tasks = [
    {"title": "任务1：寻找失踪的同学", "desc": "..."},
    {"title": "任务2：校长的邀请函", "desc": "..."},
]
for t in tasks:
    result = api_call("/game/saveTask", {
        "chapterId": 52,
        "title": t["title"],
        "taskType": "side",
        "status": "todo"
    })
    print(result.get("message"))
```

---

## curl 调用注意事项（Windows）

> **踩坑经验**：Windows 下 curl 是 `cmd.exe` 的内置命令（非 Git Bash 的 curl），行为差异极大。

### 问题1：多行命令换行符

**错误**：用 `^` 换行（cmd 风格），但 Git Bash 用 `\`。
**正确**：用 Python 脚本代替（见上方 Python 模板），或确保用 Git Bash 且用 `\` 换行。

### 问题2：JSON 里的双引号

**错误**：`--data-raw '{ "name": "value" }'`（单引号在 Windows 不生效）
**正确**：用双引号，内部 JSON 双引号加转义 `\"`，或直接用 Python。

### 问题3：`--insecure` 位置

**错误**：把 `--insecure` 放在命令中间，导致被当作独立命令执行。
**正确**：`--insecure` 必须紧跟在 `curl` 后面，或在最后。

### 推荐做法

**完全不要用 curl 调用 JSON API（Windows）**，直接用 Python `urllib` 或 `requests` 库。

---

## 已创建数据汇总

> 以下数据已在 `我的诡异表妹` 故事中创建（2026-05-28）

| 类型 | ID | 名称 | 备注 |
|------|-----|------|------|
| 世界 | 35 | 我的诡异表妹 | 已更新 settings/playerRole/narratorRole |
| 章节 | 52 | 第1章：自由章节 | 已有，已更新 content/openingRole/openingText |
| 任务 | 1-50 | 50个预选任务 | 全部创建成功，taskId=1~50 |

**下一步操作：**

1. 在 Toonflow 后台手动创建 10 个 NPC 角色（小七、校长、苏老师、裂口女、无面人、长发女、李明、王思远、赵小胖、路人甲）
2. 创建后获取各角色的 `npc_xxx` ID
3. 将角色 ID 填入 `settings.roles` 数组，再次调用 `saveWorld` 更新
4. 上传角色头像（前景/背景）到服务器
5. 上传章节背景图，更新 `backgroundPath`
6. 生成角色语音（prompt_voice）

---

## 接口
[image_api](image_api)
[voice_api](voice_api)
[save_api](save_api)

*文档版本：v1.0（2026-05-28）*
*对应 toonflow-game-app 源码版本：基于 src/routes/game/ 整理*
