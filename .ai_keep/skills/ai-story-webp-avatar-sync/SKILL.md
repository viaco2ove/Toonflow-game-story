---
name: ai-story-webp-avatar-sync
description: >-
  把本地生成的角色视频头像(.mp4)上传到 Toonflow 服务器，转成 webp 动画头像 + png
  背景，并写回世界角色数据。通常承接 ai_vedio_gen 技能（先生成 mp4，再转 webp）。
  触发词：视频转webp、mp4转webp、同步webp头像、上传视频头像、avatar video to webp。
---

# AI Story WebP 头像同步 (ai-story-webp-avatar-sync)

把本地 mp4 角色视频头像，通过服务端接口转成 webp 动画头像（含去背 foreground + 背景
background + 原视频 + 首帧），并可选写回世界角色数据。

## 何时用

- 已用 `ai_vedio_gen` 生成角色立绘视频（.mp4），需要转成游戏可用的 webp 动画头像
- 批量把多个角色视频同步成 webp 头像
- 更新世界角色的头像字段（avatarPath / avatarBgPath / avatarVideoPath）

## 数据流（不要搞混）

```
.mp4 输入来源
  → 从 {root}/.cache/character/{story}/{rolename}/ 读取（ai_vedio_gen 产出）
  → 读入内存 → base64 → 发给服务器转换
  → 服务器返回 webp 路径 → 写回世界角色数据（不走本地缓存）
```

⚠️ **webp 转换结果是直接写服务器，不落地本地 .cache 目录。**
（.cache 只存放 mp4 输入文件）
- `{root}` =  项目根目录
- `{story}` = 故事名，如 `黑塔：从超忆症开始成神`
- `{rolename}` = 角色名，如 `先生`、`张晚意`

## 本地生成方案（推荐）

用 `convert-avatar-video-to-webp` 技能——**不走接口**，直接在本地用 ffmpeg + MODNet 抠图，
产物落到 `.cache/character/{story}/{rolename}/webp/`。质量比服务端 colorkey 假抠图好。

```bash
python "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.workbuddy/skills/convert-avatar-video-to-webp/convert.py" \
  --mp4    "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.cache/character/黑塔：从超忆症开始成神/先生/先生_6s.mp4" \
  --out-dir "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.cache/character/黑塔：从超忆症开始成神/先生/webp"
```

详见 `convert-avatar-video-to-webp` 技能（`SKILL.md`）。

## 接口生成方案（备用）
接口流程（参考 api_help/image_api/webp/webp.api.md）

1. **提交转换**
   `POST /game/convertAvatarVideoToGif`
   请求体：`{"projectId":1, "fileName":"xxx.mp4", "base64Data":"data:video/mp4;base64,...."}`
   返回：`data.taskId`（用于轮询）

2. **轮询进度**
   `POST /game/convertAvatarVideoToGif/status`
   请求体：`{"taskId": <id>}`
   返回：`data.status`（running → success/failed）、`progress`、`message`
   成功时 `data` 含：
   - `foregroundFilePath` → **webp 动画头像**（去背）
   - `backgroundFilePath` → **png 背景**
   - `videoPath` → 原 mp4
   - `firstFramePath` → 首帧 png
   - `durationMs` → 时长

## 脚本入口

`src/toonflow/webp_avatar_sync.py` + CLI 子命令 `webp-sync`

| 参数 | 说明 |
|---|---|
| `--mp4` | 本地 mp4 路径（必填），从 `.cache/character/{story}/{rolename}/` 读取 |
| `--project-id` | 默认 1 |
| `--world-id` | 写回目标世界 ID（配合 --role-name） |
| `--role-name` | 写回目标角色名（配合 --world-id） |

## 调用示例

### 只转换（拿到 webp 路径，不写回）
```bash
python -m src.cli webp-sync --mp4 "{root}/.cache/character/黑塔：从超忆症开始成神/先生/先生_2026-09-04T16-41-32.mp4"
```

### 转换 + 写回世界角色
```bash
python -m src.cli webp-sync \
  --mp4 "{root}/.cache/character/黑塔：从超忆症开始成神/先生/先生_2026-09-04T16-41-32.mp4" \
  --world-id 44 \
  --role-name "先生"
```


## 完整工作流（与 ai_vedio_gen 串联）

### 方案 A：本地生成（推荐）

```
角色立绘.png
   │  ai_vedio_gen (VideoGen 图生视频，mp4 落 .cache)
   ▼
.mp4 → convert-avatar-video-to-webp (本地 ffmpeg + MODNet)
   ▼
.cache/character/{story}/{role}/webp/
   ├─ foreground.webp   ← 透明前景
   ├─ background.png    ← 静态背景
   ├─ firstFrame.png
   └─ video.mp4
```

产物可手动上传服务器，或后续走方案 B 的写回逻辑。

### 方案 B：服务端接口（原始方案）

```
角色立绘.png
   │  ai_vedio_gen (VideoGen 图生视频，mp4 落 .cache)
   ▼
.mp4 → 读入 base64 → 发给服务器转换 → webp 直接写回世界角色数据
```

## 写回机制（防重复世界 — 重要）

写回走 `client.save_world(world)`，**但必须先把 `worldId` 和 `id` 都设为目标世界 ID**
（`sync_to_role` 里 `world["id"]=world_id; world["worldId"]=world_id` 再 save_world）。
原因与坑：

- `get_world()` 返回的字段里**只有 `id`、没有 `worldId`**。
- 服务端 `saveWorld` 以 `worldId` 为准：缺 `worldId`（或 `worldId=0`）会被当成「新建世界」→
  **重复生成一个同名故事**。这正是本技能早期版本的 bug（详见下方排查表）。
- 修法就是和 `ai-story-story-sync` 的 `full_update.py` 内部写法保持一致：显式补 `worldId` 后再 save。

⚠️ **为什么写回不能直接调 `ai-story-story-sync`（`toonflow update`）**：
`ai-story-story-sync` 的 `update_npc_roles` 会**重新调用 `separate_avatar` 抠图**，
把角色的 `avatarPath` 覆盖回 png（`_fg.png`），从而**把刚生成的 webp 动画头像冲掉**。
所以 webp 写回必须用本技能的「定向 worldId-aware save_world」，只改这一个角色的 5 个头像字段，
不动其它数据、不触发抠图。`ai-story-story-sync` 负责的是「整故事推送」，二者职责不同。

## 与 ai_vedio_gen 的关系

| 技能 | 产出 | 消耗 |
|---|---|---|
| `ai_vedio_gen` | mp4 视频（落 .cache） | VideoGen credit（5s≈50-100） |
| `ai-story-webp-avatar-sync` | webp 动画头像（直接写服务器，不落本地） | 服务端转换（无额外 credit，但耗时 1-3 分钟） |

## 排查

| 症状 | 原因 | 解法 |
|---|---|---|
| 提交返回 code≠200 | mp4 损坏/超大小限制 | 检查文件，压缩到 5-10s、720P |
| status 一直 running | 转换队列拥堵 | 加大 --no-poll-limit（默认 360s） |
| status=failed | 服务端抠图模型失败（多角色/复杂背景） | 先抠图再生成视频，或简化立绘 |
| 写回后头像不显示 | 客户端拼 host 问题 | webp 路径是相对路径 `/1/game/role/...`，客户端自动拼 BASE_URL；确认世界已发布 |
| 找不到角色 | role-name 拼写 | get_world 确认 settings.roles 里的 name 字段 |
| **写回后出现两个同名故事** | `save_world` 漏了 `worldId` → 服务端当新建 | `sync_to_role` 已补 `worldId`；若仍发生，删掉残缺的那个（chapterCount=0、`listWorlds` 比对），用 `deleteWorld` 删 `worldId`，再把 webp 字段从被删世界抄回正确世界（见脚本顶层说明） |
| 写回后 webp 变成静态 png | 误走 `toonflow update` 重跑抠图覆盖 | webp 写回必须用本技能定向 save_world，不要经 `ai-story-story-sync` |
