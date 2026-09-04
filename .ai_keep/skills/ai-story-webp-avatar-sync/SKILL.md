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

## 接口流程（参考 api_help/image_api/webp/webp.api.md）

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
| `--mp4` | 本地 mp4 路径（必填） |
| `--project-id` | 默认 1 |
| `--world-id` | 写回目标世界 ID（配合 --role-name） |
| `--role-name` | 写回目标角色名（配合 --world-id） |

## 调用示例

### 只转换（拿到 webp 路径，不写回）
```bash
python -m src.cli webp-sync --mp4 "ai_story/android_sj/黑塔：从超忆症开始成神/.cache/character/黑塔：从超忆症开始成神/先生/先生_2026-09-04T16-41-32.mp4"
```



## 完整工作流（与 ai_vedio_gen 串联）

```
角色立绘.png
   │  ai_vedio_gen (VideoGen 图生视频)
   ▼
角色.mp4 (5s)
   │  ai-story-webp-avatar-sync (本技能)
   ▼
webp 动画头像 + png 背景 ──》缓存到 {root}/.cache/character/{story}/{rolename}/──》
调用技能：ai-story-story-sync
```

## 与 ai_vedio_gen 的关系

| 技能 | 产出 | 消耗 |
|---|---|---|
| `ai_vedio_gen` | mp4 视频 | VideoGen credit（5s≈50-100） |
| `ai-story-webp-avatar-sync` | webp 动画头像 | 服务端转换（无额外 credit，但耗时 1-3 分钟） |

## 排查

| 症状 | 原因 | 解法 |
|---|---|---|
| 提交返回 code≠200 | mp4 损坏/超大小限制 | 检查文件，压缩到 5-10s、720P |
| status 一直 running | 转换队列拥堵 | 加大 --no-poll-limit（默认 360s） |
| status=failed | 服务端抠图模型失败（多角色/复杂背景） | 先抠图再生成视频，或简化立绘 |
| 写回后头像不显示 | 客户端拼 host 问题 | webp 路径是相对路径 `/1/game/role/...`，客户端自动拼 BASE_URL；确认世界已发布 |
| 找不到角色 | role-name 拼写 | get_world 确认 settings.roles 里的 name 字段 |
