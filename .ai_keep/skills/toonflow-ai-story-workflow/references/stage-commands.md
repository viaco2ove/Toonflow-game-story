# 各阶段精确命令与产物

> 工作目录统一为项目根目录；以下 `<python>` 指装有 `requests / PyYAML / Pillow / onnxruntime / torch` 的解释器（当前可用：服务仓 `tools/avatar-matting/birefnet/venv/Scripts/python.exe`，勿用裸沙箱或全局解释器跑 CLI）。所有 `--story <故事名>` 可省略，省略时读 `.env` 的 `CURRENT_STORY`。

## 目录与文件约定

| 类别 | 路径 |
|---|---|
| 故事目录 | `ai_story/<分组>/<故事名>/`：`STORY.md`、`story.json`、`roles/`、`avatars/`、`chapters/`、`image/`、`tasks/`、`worldbook/` |
| 角色素材缓存 | `.cache/character/<故事名>/<角色目录>/` |
| 立绘 mp4 | `.cache/character/<故事名>/<角色目录>/<角色>_立绘微动.mp4` |
| 音色 wav | `.cache/character/<故事名>/<角色目录>/<角色>_voice.wav`（玩家目录为 `用户/用户_voice.wav`） |
| 本地 webp 产物 | `.cache/character/<故事名>/<角色目录>/webp/`：`foreground.webp`、`background.png`、`firstFrame.png`、`video.mp4`、`webp.json` |
| 拉回复核目录 | `ai_story/<分组>/<故事名>/toonflow_agme_cache/` |

> 玩家角色：目录固定 `用户/`，CLI 用 `--role-name <story.json.player_role.name>` + `--is-player`；玩家无 `avatarVideoPath` 字段。

---

## A1 数据生成（本地，不触网）

### 校验 story.json / 章节 / 世界书

按 `/ai-story-data-gen` 校验清单跑断言；世界书 MD 改过后重建 JSON：

```bash
<python> -m src.cli toonflow worldbook-build --story "<故事名>"
```

### 列出现有故事（核对目录名）

```bash
<python> -m src.cli list-stories
```

## A5 本地 mp4 → webp 四件套

配置文件：`.workbuddy/config/vedio_to_webp.yml`（模型/帧率/边长以配置为准，不擅自改）。任务 JSON：

```json
{
  "input_video": ".cache/character/<故事名>/<角色>/<角色>_立绘微动.mp4",
  "rolename": "<远端角色名>",
  "rolenType": "npc",
  "story": "<故事名>",
  "type": "living",
  "output_path": ".cache/character/<故事名>/<角色>/webp/"
}
```

```bash
<python> -m src.cli webp --living .workbuddy/config/vedio_to_webp.yml .cache/tasks/<角色>_webp.json
# 帧产物损坏需重跑时带 --tmp_frames 让脚本自清重抽：
<python> -m src.cli webp --living --tmp_frames .workbuddy/config/vedio_to_webp.yml .cache/tasks/<角色>_webp.json
```

本地复核：`webp/webp.json` 的 `frames` 与 `foreground.webp` 的 ANMF 帧数一致；容器为 VP8X 动态图（静态 VP8L 即失败，见 pitfalls）。

---

## B1 主体上传（世界 / 玩家 / NPC / 章节 / 封面）

```bash
<python> -m src.cli toonflow update --story "<故事名>"
```

内部顺序：建/更世界 → 玩家角色 → NPC + 头像分离 → 章节 → 封面/背景图 → `save_world`。首次 `world_id=0` 时新建世界并回写 `story.json`。

### 复核：世界数据

```bash
<python> -m src.cli toonflow world --story "<故事名>" --op get
```

核对返回结构（`getWorld` 顶层与 `settings` 分层，勿取错字段）：

- 顶层 `id` 即世界 ID；`getWorld` 不回 `worldId` 属正常（写回时才需补）。
- 顶层 `playerRole`、`narratorRole` 存在；`settings.roles` 是 **NPC 列表**（不含玩家/旁白），数量 = 本地 NPC 数。
- 章节看顶层 `chapterCount` 与 `settings.chapterExtras[]`（不是 `d.chapters`），数量与本地章节数一致；每条 extra 的 `background` / `coverPath` 非空。
- 封面 `coverPath` 非空。

### 复核：单章节

```bash
<python> -m src.cli toonflow chapters --story "<故事名>" --op getChapter --entry-id <章节ID>
```

---

## B2 音色绑定

```bash
<python> -m src.cli workflow voice-file-up-save \
  --story "<故事名>" --role-name "<角色名>" \
  --audio ".cache/character/<故事名>/<角色>/<角色>_voice.wav" \
  --voice-mode clone --reference-text "" --project-id 1
# 玩家加 --is-player
```

备用直传接口（先传音频再 save 世界，正常走不上）：

```bash
<python> -m src.cli toonflow client --op uploadAudio --entry "<wav 路径>" --project-id 1
```

### 复核

角色记录含 `voiceMode=clone`、`voiceReferenceAudioPath=/1/voice/<uuid>.wav`，参考音 `GET {BASE_URL}/1/voice/<uuid>.wav` 返回 200。

---

## B3 webp 动画头像写回（定向 save_world，禁止再跑 update）

```bash
<python> -m src.cli workflow role-webp-avatar \
  --story "<故事名>" --role-name "<角色名>" \
  --webp  ".cache/character/<故事名>/<角色>/webp/foreground.webp" \
  --bg    ".cache/character/<故事名>/<角色>/webp/background.png" \
  --first-frame ".cache/character/<故事名>/<角色>/webp/firstFrame.png" \
  --video ".cache/character/<故事名>/<角色>/webp/video.mp4" \
  --duration-ms <webp.json.durationMs> --project-id 1
# 玩家加 --is-player，且不传 --video / --duration-ms
```

备用接口式同步：

```bash
<python> -m src.cli webp-sync --mp4 "<mp4 路径>" --world-id <世界ID> --role-name "<角色名>"
```

### 复核

角色记录含 `avatarPath`（webp）、`avatarBgPath`、`avatarFirstFramePath`；NPC 另含 `avatarVideoPath` + `avatarDurationMs`；拉回的 `avatar.webp` 体积与本地 `foreground.webp` 接近。写回后**不应出现第二个同名世界**。

---

## B4 章节封面 / 背景图绑定

```bash
<python> -m src.cli workflow chapter-background-img \
  --story "<故事名>" --chapter-id <章节ID> \
  --background "image/chapter_<N>_bg.png" --project-id 1
# 需要章节封面时加 --cover "<png 路径>"
```

### 复核

章节一级字段 `backgroundPath`（封面 `coverPath`）非空；`settings.chapterExtras[]` 对应章节的 `background` 非空。

---

## B5 世界书导入

```bash
# 改了源 MD 先重建
<python> -m src.cli toonflow worldbook-build --story "<故事名>"
# 导入：默认 replace 全量覆盖；merge 为追加
<python> -m src.cli toonflow worldbook --story "<故事名>" --op import --mode replace
# 复核条数（唯一判据）
<python> -m src.cli toonflow worldbook --story "<故事名>" --op list
```

其他世界书操作：`--op export`（拉回本地）、`--op save_create|save_update --entry '<json>'`、`--op delete --entry-id <id>`、`--op getWorld`。

### 复核判据

`list` 返回的实际条目数 == 本地 `worldbook.json.entries.length`。import 返回 200 / `imported=0` 不代表成功（批量吞错假成功），**只认 list 条数**。

---

## C1 拉回远端数据复核

```bash
<python> -m src.cli agme_cache --story "<故事名>" --world-id <世界ID>
# world_id 省略时从 story.json 读；story 省略时用 CURRENT_STORY
<python> -m src.cli agme_cache
```

落地结构：`metadata.json`、`images/world_cover.jpg`、`avatars/<角色>/role.json + original.png + avatar.webp + background.png`、`chapters/chapter_N.json + chapter_N_<标题>.md + backgrounds/chapter_N.png`。

### 逐项核对

| 核对项 | 位置 / 字段 |
|---|---|
| 角色数量 | `avatars/` 目录数 = 玩家 + 旁白 + NPC |
| 音色 | `role.json.voiceMode`、`voiceReferenceAudioPath`（clone 参考音不进 cache 下载，无 `voice.wav` 属正常） |
| 头像 | `avatarPath` / `avatarBgPath` / `avatarFirstFramePath`；NPC `avatarVideoPath` + `avatarDurationMs` |
| 章节 | `chapters/` JSON + MD 配对，背景图落地 `backgrounds/` |
| 世界封面 | `images/world_cover.jpg` 非空 |

> 远端两章 `sort` 相同时，本地按列表顺序编号（chapter_1 / chapter_2），编号可能与章节序号对调，以 JSON 内 `title` / `sort` 为准。
