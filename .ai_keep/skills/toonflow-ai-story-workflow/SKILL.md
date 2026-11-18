---
name: toonflow-ai-story-workflow
description: Toonflow 互动故事端到端流水线编排技能。把一个新故事从设定收集、本地数据与素材生产（章节/角色 JSON、头像 PNG、音色 wav、立绘 mp4、webp 动画头像），到服务端同步（世界/玩家/NPC/章节/封面/音色/webp/章节图/世界书），再到 agme_cache 拉回复核，按固定顺序串联并设闸门。触发词：整条故事流水线、从头做一个故事、故事发布流程、同步故事到服务器、故事到哪一步了、接着做这个故事、补齐故事素材、ai-story workflow、toonflow 全流程。
location: user
agent_created: true
tags:
  - toonflow
  - story-workflow
  - orchestration
  - publish
---

# Toonflow 故事端到端流水线编排

使用例子 
- /toonflow-ai-story-workflow 漫剧《末世选择，从解析神明开始成神》 - 免费好剧，尽在红果
点击链接打开👉https://novelquickapp.com/s/pPK-RrDKEz8/
复制本条消息后，打开「红果短剧App」后免费看全集~
- /toonflow-ai-story-workflow 完成到那一步了

## 1. 这个技能做什么 / 不做什么

**做编排**：把一个故事从「想法 → 本地数据/素材 → 服务端 → 复核」按固定顺序串起来，规定每个阶段的输入、产物、复核闸门与顺序依赖。

**不重写子技能知识**：章节格式、生图/生视频/音色通道选择、抠图参数等细节，一律读对应子技能的 `SKILL.md`，本文件只做路由与顺序约束。

### 红线（全程遵守）

- **不允许 AI 自行换生图/生视频/音色通道或模型**，以配置文件为准；发现问题可提方案，不能自以为是。
- **写服务端的操作（update / 各类 save_world / worldbook import）是真实变更**，执行前需用户明确许可。
- 测试/临时脚本只放项目 `.cache/` 下；**不允许自行 commit / push**；首行带 `@no_modify` 的文件不可改。
- 角色名、文件名、目录名必须与 `story.json`、`roles/`、`avatars/` 实际文件一致，不臆造。

## 2. 环境与入口

| 项 | 约定 |
|---|---|
| 工作目录 | 项目根目录（CLI 以根目录为 cwd，读根目录 `.env` 与 `src/`） |
| 故事目录 | `ai_story/<分组>/<故事名>/`，内含 `STORY.md`、`story.json`、`roles/`、`avatars/`、`chapters/`、`image/`、`tasks/`、`worldbook/` |
| 服务端配置 | 根目录 `.env`：`BASE_URL`、`TOKEN`、`user_name`、`user_psw`、`CURRENT_STORY`；token 失效时客户端用账号密码自动重登并回写 `TOKEN` |
| CLI 前缀 | `<python> -m src.cli ...`（具体解释器与命令参数见 `references/stage-commands.md`） |
| 角色素材缓存 | `.cache/character/<故事名>/<角色目录>/`：立绘 `<角色>_立绘微动.mp4`、音色 `<角色>_voice.wav`、`webp/` 子目录 |

> 玩家角色目录固定为 `用户/`，远端角色名以 `story.json.player_role.name` 为准；NPC 目录名 = 远端角色名 = 文件名 stem。

## 3. 阶段总览

| 阶段 | 子技能（slash） | 输入 | 产物 / 落点 | 复核闸门 |
|---|---|---|---|---|
| **A0 前置设定** | `/ai-story-chat-pre` | 用户的故事想法 | `.cache/chat_pre/<故事名>/<故事名>.md`《故事设定集》 | 设定集字段无「待补」，用户确认 |
| **A1 数据生成** | `/ai-story-data-gen` | 设定集 | `story.json`、`chapters/chapter_N.json + .md`、`worldbook/worldbook.json` | 三类 JSON 齐全；`content == md`；校验清单全过 |
| **A2 章节内容** | `/toonflow-chapter-design` | 设定集大纲 | 章节 MD + JSON（7 字段） | 无 H4、阶段名唯一、每阶段有 `### 用户发言` |
| **A3 图像素材** | `/ai-image-gen` | 头像/封面/背景提示词 | `avatars/<角色>.png`、`image/cover.png`、`image/chapter_N_bg.png` | 头像 PNG 与 `story.json.avatar_file` 一一对应 |
| **A4 音色素材** | `/ai_voice_gen` | 音色提示词 | `.cache/character/<故事>/<角色>/<角色>_voice.wav` | 15–50s、<20MB、24000Hz、16bit |
| **A5 立绘视频 → webp** | `/ai_vedio_gen` → `/convert-avatar-video-to-webp` | 头像 PNG | `.cache/.../<角色>/<角色>_立绘微动.mp4` → `webp/` 四件套 + `webp.json` | webp 为 VP8X 动态图，ANMF 帧数 == `webp.json.frames` |
| **B1 主体上传** | `/ai-story-story-sync` | A1–A3 本地数据 | 远端世界 + 玩家 + NPC + 章节 + 封面；回写 `world_id` | `toonflow world --op get` 命中同一世界，章节/角色数对得上 |
| **B2 音色绑定** | `/ai-story-voice-sync` | A4 的 wav | 远端角色 `voiceMode=clone` + 参考音路径 | 角色 `voiceReferenceAudioPath` 非空，参考音可下载 |
| **B3 webp 头像写回** | `/ai-story-webp-avatar-sync` | A5 的 `webp/` | 远端角色 `avatarPath/avatarBgPath/avatarFirstFramePath`（NPC 另绑视频 + 时长） | 拉回的 `avatar.webp` 与本地一致；**不出现重复世界** |
| **B4 章节背景图** | `/ai-story-chapte-img-sync` | A3 背景图 | 章节 `backgroundPath` + `settings.chapterExtras` 背景 | 两章背景路径非空 |
| **B5 世界书导入** | `/ai-world-book-sync` | A1 的 `worldbook.json` | 远端世界书条目 | **`worldbook --op list` 实际条数 == 本地条目数**（唯一判据） |
| **C1 拉回复核** | `/toonflow_agme_cache` | 远端世界 | `toonflow_agme_cache/`（角色/章节/封面/头像/背景） | 角色数、章节数、图片落地；字段完整 |

## 4. 硬顺序依赖（不可调换）

1. **本地数据与素材齐备后才能跑 B1 `update`**；缺 `story.json` / 章节 JSON / 头像 PNG 时先回 A1–A3 补齐。
2. **B1 `update` 必须先于 B5 世界书导入**：导入依赖 `story.world_id`，为空会直接抛错；首次 `update` 会新建世界并把 `world_id` 回写 `story.json`。
3. **B3 webp 写回必须走定向 `save_world`**，写完之后**禁止再跑 `toonflow update`**——`update_npc_roles` 会重新抠图，把动画 webp 冲回静态 PNG。
4. B2 音色、B3 webp、B4 章节图相互独立，可在 B1 之后单独重跑；B5 世界书也可单独重跑。
5. **C1 复核永远放在最后**；任何阶段重写远端后都应重新拉一次 cache 核对。

## 5. 各阶段要点（路由到子技能）

### A 本地创作

- **A0 前置设定**：一次只问 1–3 个问题，模糊处追问具体化；收齐 11 个板块后输出设定集并请用户确认。详见 `/ai-story-chat-pre`。
- **A1 数据生成**：写 `story.json`（世界/角色/章节封面映射）、章节 JSON+MD 配对、世界书 MD → `worldbook.json`；角色从 `roles/*.md` 解析，不读角色 JSON。详见 `/ai-story-data-gen`。
- **A2 章节内容**：`##` 阶段 + `###` 事件 + `### 用户发言`；背景提示词与成功条件进 JSON，MD 保持纯净正文。详见 `/toonflow-chapter-design`。
- **A3 图像**：角色头像中景单人全身；封面可叠角色；章节背景推荐无具体角色。详见 `/ai-image-gen`。
- **A4 音色**：wav 落角色缓存目录，规格见 `/ai_voice_gen`。
- **A5 立绘视频 → webp**：视频固定机位、无运镜、9:16、720P、5–10s；本地 ffmpeg + 抠图模型产出 `webp/` 四件套。详见 `/ai_vedio_gen`、`/convert-avatar-video-to-webp`。

### B 服务端同步

- **B1 主体上传**：一条命令五合一（世界/玩家/NPC/章节/封面）。详见 `/ai-story-story-sync`。
- **B2 音色绑定**：逐角色上传 wav 并绑定到玩家/NPC。详见 `/ai-story-voice-sync`。
- **B3 webp 写回**：逐角色把本地 `webp/` 写回远端；玩家无视频字段。详见 `/ai-story-webp-avatar-sync`。
- **B4 章节背景图**：按章节 ID 绑定封面/背景。详见 `/ai-story-chapte-img-sync`。
- **B5 世界书**：先 `worldbook-build`（若改了源 MD）再 `import`；**导入后必须 `list` 复核条数**。详见 `/ai-world-book-sync`、`/ai-story-story-sync`。

### C 复核

- **C1 拉回 cache**：把远端世界完整数据拉到本地 `toonflow_agme_cache/`，逐项核对角色、章节、封面、头像、背景。详见 `/toonflow_agme_cache`。

## 6. 发布前检查清单

- [ ] `.env` 的 `BASE_URL` / 账号正确，指向目标环境（本地 / 生产）
- [ ] `story.json` 字段完整，`player_role` + `npc_roles` 的 `md_file` / `avatar_file` 与实际文件一一对应
- [ ] 章节 JSON 7 字段齐全，`content` 与配对 MD 完全一致，MD 无 `## 章节背景图` 块、无 `> 成功条件` 行
- [ ] `worldbook/worldbook.json` 存在且 `entries` 非空、无空内容条目
- [ ] 头像 PNG、封面、章节背景图就位；音色 wav、立绘 mp4、`webp/` 四件套就位
- [ ] B1 后 `world_id` 已回写；B5 后 `list` 条数与本地一致；C1 cache 角色数 / 章节数 / 图片落地齐全

## 7. 子技能导航

| slash 命令 | 技能目录 | 用途 |
|---|---|---|
| `/ai-story-chat-pre` | `ai-story-chat-pre` | 前置设定收集 |
| `/ai-story-data-gen` | `ai-story-data-gen` | 生成 story.json / 章节 JSON / 世界书 JSON |
| `/toonflow-chapter-design` | `toonflow-chapter-design` | 章节正文与阶段结构设计 |
| `/ai-image-gen` | `ai-image-gen` | 头像 / 封面 / 章节背景图 |
| `/ai_voice_gen` | `ai_voice_gen` | 角色音色 wav |
| `/ai_vedio_gen` | `ai_vedio_gen` | 立绘微动 mp4 |
| `/convert-avatar-video-to-webp` | `convert-avatar-video-to-webp` | 本地 mp4 → webp 四件套 |
| `/ai-story-story-sync` | `ai-story-story-sync` | 主体上传 + 世界书导入入口 |
| `/ai-story-voice-sync` | `ai-story-voice-sync` | 音色上传绑定 |
| `/ai-story-webp-avatar-sync` | `ai-story-webp-avatar-sync` | webp 动画头像写回 |
| `/ai-story-chapte-img-sync` | `ai-story-chapte-img-sync` | 章节封面 / 背景图绑定 |
| `/ai-world-book-sync` | `ai-world-book-sync` | 世界书同步 |
| `/toonflow_agme_cache` | `toonflow_agme_cache` | 拉取远端数据复核 |

## 8. 参考文件

- [`references/stage-commands.md`](references/stage-commands.md) — 各阶段精确 CLI 命令、参数、产物路径与复核探针。
- [`references/pitfalls.md`](references/pitfalls.md) — 跨阶段假成功陷阱、卡点排障与远端 schema 问题。
