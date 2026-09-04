# toonflow_agme_cache

将 Toonflow 服务端世界的完整数据**拉取到本地** `toonflow_agme_cache/` 目录，
完全模仿「谁让这个山大王修仙的/toonflow_agme_cache」的结构。

---

## 触发词

- 拉取 agme_cache、拉取服务端数据、拉到 agme_cache
- 下载 toonflow_agme_cache、pull agme_cache、agme cache
- 把服务器数据拉到本地

---

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `story` | string | 推荐 | 故事名（精确匹配目录名） |
| `world_id` | int | 推荐 | world ID（不指定则从 `story.json` 读） |

> 两个参数都省略时：取 `.env` 中的 `CURRENT_STORY`，world_id 从 `ai_story/android_sj/{故事名}/story.json` 读。

---

## 执行命令

```bash
# 完整指定
python -m src.cli agme_cache --story "黑塔：从超忆症开始成神" --world-id 44

# 用 CURRENT_STORY（不传 story）
python -m src.cli agme_cache --world-id 44

# 完全不传（自动读 CURRENT_STORY + story.json.world_id）
python -m src.cli agme_cache
```

---

## 输出目录结构

```
{story_dir}/toonflow_agme_cache/
├── metadata.json           # 拉取元信息（world_id、pulled_at 等）
├── images/
│   └── world_cover.jpg     # 世界封面（服务端下载）
├── avatars/{name}/
│   ├── original.{ext}      # 本地原始头像（从 avatars/ 目录复制）
│   ├── avatar.webp         # 服务端抠图头像（下载）
│   ├── background.png      # 服务端抠图背景（下载）
│   ├── role.json           # 服务端角色完整数据（含 parameterCardJson 等）
│   └── voice.wav           # 服务端生成的音色（下载）
├── chapters/
│   ├── backgrounds/
│   │   ├── chapter_1.png
│   │   └── chapter_2.png
│   ├── chapter_1.json      # 服务端原始章节数据
│   ├── chapter_1_{title}.md  # content 转为 Markdown
│   ├── chapter_2.json
│   └── chapter_2_{title}.md
```

**`role.json` 字段说明**（与服务端 `getWorld().settings.roles[]` 一致）：

| 字段 | 说明 |
|---|---|
| `id` | 角色标识（如 `npc_1`） |
| `name` | 角色名 |
| `roleType` | `npc` / `player` / `narrator` |
| `avatarPath` | 服务端抠图头像路径 |
| `avatarBgPath` | 服务端抠图背景路径 |
| `avatarSourcePath` | AI 生图原图路径（若有） |
| `voiceGeneratedDownloadUrl` | 生成的语音下载地址 |
| `voice` | 语音提示词 |
| `voicePromptText` | 音色提示词 |
| `parameterCardJson` | 角色参数卡 JSON（等级/境界/技能/物品等） |

---

## 依赖接口

| 操作 | 接口 |
|---|---|
| 拉取世界数据 | `POST /game/getWorld` |
| 拉取章节列表 | `POST /game/getWorld` → `chapters[]` |
| 下载角色头像/背景 | `GET {BASE_URL}{path}`（`Authorization: Bearer`） |
| 下载音色 | `GET {voiceGeneratedDownloadUrl}` |
| 下载章节背景 | `GET {BASE_URL}{backgroundPath}` |

---

## 文件路径解析规则

```
服务端路径: /1/game/role/xxx.webp
下载 URL:   {BASE_URL}/1/game/role/xxx.webp   （BASE_URL 从 .env 读取）
```

**host 重写（重要）**：服务端数据库里存的文件 URL 可能带旧 host（如换服务器前的 `10.10.2.195`，或 `127.0.0.1`）。
`agme_cache.py` 的 `_rebase_url()` 会把所有下载 URL 的 host 统一重写为 `.env` 里 `BASE_URL` 的 host（保留 path 和 query）。
语音 `audioProxy` URL 必须保留 query（`configId`/`source`/`token`），否则下载 404。

---

## 已知限制

- **服务端必须可达**：确保 `.env` 的 `BASE_URL` 指向实际部署地址且网络可达
- **token 过期**：客户端会在 token 失效时自动重新登录，登录失败会报错 `用户名或密码错误`
- **无 download API**：文件下载走 `GET {BASE_URL}{path}`，若服务器对静态文件有路径保护可能失败
- **章节 sort 重复**：服务端 sort 值可能重复，本地文件按列表顺序编号（chapter_1、chapter_2…），以 sort 排序为准

---

## 排查表

| 症状 | 原因 | 解法 |
|---|---|---|
| `ConnectTimeoutError` | 服务端不可达 | 确认 `BASE_URL` 与网络连通性（ping 服务器 IP） |
| `用户名或密码错误` | TOKEN 过期且 re-login 失败 | 确认 `.env` 中 `user_psw` 正确 |
| `下载失败: http://旧IP/...` | DB 里存的 URL 带旧 host | 已由 `_rebase_url` 自动重写；若仍失败检查 BASE_URL |
| `下载失败: .../voice/audioProxy` | 重写 host 时丢了 query 参数 | 已修复（保留 query）；确认 `voiceGeneratedDownloadUrl` 里的 token 未过期 |
| `下载失败: /1/game/xxx` | 静态文件 404 | 服务端路径不存在，检查 world 数据中 path 是否正确 |
| `original.png` 未生成 | 本地 `avatars/` 无匹配文件 | 手动确认 `{story_dir}/avatars/` 下有对应角色图片 |
| voice.wav 未下载 | 服务端未生成音色 | 检查 `voiceGeneratedDownloadUrl` 是否为空 |
