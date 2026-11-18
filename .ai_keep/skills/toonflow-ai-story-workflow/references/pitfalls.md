# 跨阶段陷阱与卡点排障

> 按阶段归类。详细机理以对应子技能 `SKILL.md` 为准；本文件只列编排时必须盯住的「假成功 / 不可逆 / 易返工」点。

## B5 世界书

### 1. import 假成功：返回 200 / `imported=0`，远端一条没进去

- **判据**：判断导入成功的**唯一标准**是 `worldbook --op list` 的实际条数，不是 import 命令退出码或返回值。
- **根因**：服务端 `importWorldBook` 逐条吞错，全部失败也返回 `code=200`、`imported=0`。
- **排障**：用 `--op save_create --entry '<单条 json>'` 打探针，暴露底层真实报错。

### 2. 远端库 schema 滞后：缺列导致插入失败

- **症状**：探针报 `SQLITE_ERROR: table t_worldBook has no column named <列>`（实测缺过 `agentList`、`stickiness`）。
- **根因**：服务端代码保存时必写该列，但老部署的 `ensureTable` 只建表不补列，仓库迁移没跟上；远端老库 schema 滞后于代码。
- **`stickiness` 事实**：整数，缺失时回退 `WORLD_BOOK_STICKINESS_DEFAULT = 3`（见服务仓 `src/constants/gobal.const.ts`）；插入列顺序含 `agentList, category, constant, content, createTime, entryId, group, keys, order, probability, selectiveKeys, selectiveLogic, sort, stickiness, title, updateTime, worldId`。
- **解法**（服务端侧，本地客户端绕不过）：参照 `src/migrations/20260901_000001_add_worldbook_agentlist.js` 补一个幂等 knex 迁移（`hasTable` / `hasColumn` 守卫 + `alterTable`），部署/重启远端实例使 `migrate.latest()` 生效；之后回故事目录重跑 import 并 `list` 复核。
- **不可用的旁路**：`clearDatabase` 会 rollback + 清库，严禁用于补列；本机所有 `db.sqlite` 副本都不含远端世界时，不要在本地库上改 schema 期待生效。

### 3. 数量翻倍

- 用了 `--mode merge` 且远端已有旧条目 → 改回默认 `replace` 全量覆盖。

## B3 webp 头像写回

### 4. 写完后禁止再跑 `toonflow update`

- **症状**：刚写回的动画 webp 变成静态 PNG。
- **根因**：`update_npc_roles` 会重新调 `separate_avatar` 抠图，把 `avatarPath` 覆盖回 png（`_fg.png`）。
- **解法**：webp 写回只用定向 `workflow role-webp-avatar`（只改这一个角色的头像字段，不触发抠图）；主体推送和头像写回职责分开。

### 5. 写回后冒出第二个同名世界

- **根因**：`get_world()` 返回字段只有 `id`、没有 `worldId`；服务端 `saveWorld` 以 `worldId` 为准，缺 `worldId`（或为 0）被当成新建世界。
- **解法**：写回前显式把 `world["id"]` 和 `world["worldId"]` 都设为目标世界 ID（`sync_to_role` 已按此实现）。若已产生残缺世界（`chapterCount=0`），用 `deleteWorld` 删除后把 webp 字段抄回正确世界。

### 6. settings 出现 MB 级 base64 脏数据

- **历史事故**：立绘 base64 被塞进 `avatarUrl/avatarMiddleUrl/avatarBackgroundUrl/avatarThumbUrl` 四字段，单条 settings 上百 MB。
- **防护**：`ToonflowClient.save_world()` 内置 `_sanitize_world_payload()` 钩子，写回前自动剥离 >4096 字符且符合 base64 字符集的字段（打印 `⚠ 剥离 base64 字段 ...`）；渲染走 `avatarPath` 相对路径，不依赖这四个 `*Url` 字段。
- **若远端库已存脏数据**：需服务端 db 侧跑幂等清理脚本，本地 save_world 不会回填已剥离字段。

## A5 本地 webp 转换

### 7. 产出 webp 完全不动（静态图）

- **唯一 smoking gun**：日志 `disposalPatched: 0`；产物容器为静态 `VP8L` 而非 `VP8X + ANMF`。
- **根因链**：`matte/` 帧序号断档（缺帧）→ `norm/` 同样断档 → ffmpeg image2 解复用器遇断档立即停止 → 只读 1 帧 → 输出静态 VP8L。
- **排障三步**：① 检测 `src/matte/norm` 帧号 min..max 是否连续；② `ffmpeg -framerate <fps> -i norm/frame_%04d.png -f null -` 反推实际读到帧数；③ 解析 webp 容器类型并数 ANMF 块。
- **守卫**：禁止手动往 `src/matte/norm` 塞帧；重跑走完整 `--tmp_frames` 让脚本自清重抽。
- **`-lossless 1` 无罪**：它是 `-c:v libwebp_anim` 帧间差分可逆性的前提，不可擅自移除；静态图元凶永远是帧序号断档。

## B2 音色

### 8. clone 模式参考音不会被 agme_cache 下载

- **现象**：`toonflow_agme_cache` 角色目录里没有 `voice.wav`。
- **根因**：cache 只下载 `voiceGeneratedDownloadUrl` 指向的服务端生成音；clone 参考音存 `voiceReferenceAudioPath=/1/voice/<uuid>.wav`，不在下载范围。
- **判据**：`role.json` 里 `voiceMode=clone` + `voiceReferenceAudioPath` 非空、参考音 `GET` 返回 200，即绑定成功；无 `voice.wav` 属正常。

## A1 / A2 章节数据

### 9. 章节 JSON 与 MD 不同步

- 改完 `chapters/*.md` 必须同步更新对应 `chapter_N.json` 的 `content`（首行 `# 标题` 全文一致）；上传读 `content`，MD 仅作人读备份。
- 背景提示词放 JSON `backgroundPrompt`，MD 禁写 `## 章节背景图` 块；成功条件放 `completionCondition`，MD 禁写 `> 成功条件` 行——否则 md_parser 降级会把标题残留进 `content` 污染正文。
- 格式红线：禁 H4；`##` 阶段名一章内唯一；`### 用户发言` 不得为空；非事件用半角冒号；旁白不替用户说话；任务分类不用 `---` 分隔。

## 环境 / 网络

### 10. token 失效或连接失败

- token 失效时客户端用 `.env` 的 `user_name / user_psw` 自动重登并回写 `TOKEN`；若报「用户名或密码错误」，先核对 `.env` 账号密码。
- `ConnectTimeoutError`：核对 `BASE_URL` 指向的目标环境与网络连通性，勿把本地 `127.0.0.1:60002` 当成生产。

### 11. 下载 URL 带旧 host / 语音 404

- DB 里存的文件 URL 可能带旧 host，`agme_cache._rebase_url()` 会把 host 统一重写到 `.env` 的 `BASE_URL`（保留 path 和 query）。
- 语音 `audioProxy` URL 必须保留 query（`configId/source/token`），丢 query 会 404。

### 12. 章节编号对调

- 远端两章 `sort` 重复时，本地按列表顺序编号（chapter_1 / chapter_2），可能与章节序号对调；以 JSON 内 `title` / `sort` 为准，不是本地文件名序号。

## 通用红线

- **不自行换通道 / 换模型**：生图、生视频、音色通道以配置文件为准；发现问题可提方案，不能自以为是。
- 测试 / 临时脚本只放 `.cache/`；**不自行 commit / push**；首行 `@no_modify` / `# @no_modify` 的文件不可改。
- 写服务端前确认目标环境；`replace` 模式世界书导入会先清远端旧条目，确认无误再跑。
