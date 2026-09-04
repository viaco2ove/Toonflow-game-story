---
name: ai-story-data-gen
description: 为 Toonflow 互动故事生成"上传所需的所有 JSON 数据"——story.json（世界配置）、chapters/chapter_N.json（章节，JSON+MD 配对）、worldbook/worldbook.json（世界书）。当用户要新建/补齐故事的可上传数据、说"补全上传故事的 json""生成故事数据"，或新故事只写了 MD 没配 JSON 时使用。对齐 src/toonflow 上传脚本（full_update / chapters / covers / worldbook_builder）的真实契约。
---

# AI Story Data Gen（故事数据生成）

## 何时使用

- 新建一个 Toonflow 故事，需要补齐全部可上传的 JSON
- 已有故事目录（只有 roles/*.md、chapters/*.md、image/*）但缺 JSON 配置
- 用户说："补全上传故事需要的 json""生成故事数据""把故事数据补齐"
- 参考榜样：`ai_story/171/谁让这个山大王修仙的`（含 worldbook 96 条）、`ai_story/android_sj/黑塔：从超忆症开始成神`（本技能实战样例）

## 上传流程读取哪些 JSON（契约）

`src/toonflow/full_update.py` 一键上传读取：

| JSON | 读取方 | 说明 |
|------|--------|------|
| `story.json` | `config.load_story_config` | 世界/角色/章节封面映射总配置，**必需** |
| `chapters/chapter_N.json` | `chapters.py` | 章节结构化数据（**JSON 优先于同名 MD**） |
| `worldbook/worldbook.json` | `storyworld/worldbook.py` | 世界书条目（`toonflow worldbook --op import` 独立上传） |
| （角色无需 JSON） | `roles.py` | 角色从 `roles/*.md` 解析（`parse_role_md`），不读 JSON |
| （封面无需 JSON） | `covers.py` | 封面/背景按 `image/` 目录 glob 匹配（`cover.*`、`chapter_N_bg.*`） |

> ⚠️ **易漏项**：新手常只写 `story.json` + 章节 MD，漏掉 `worldbook/worldbook.json`（山大王有，黑塔最初也缺）。校验时务必确认三类 JSON 齐全。

---

## 1. story.json（世界总配置）

位置：`{故事目录}/story.json`。由 `config.load_story_config` 读取。

**字段契约**（缺字段上传会报错或落空）：

```json
{
  "story_name": "故事名",
  "world_id": 0,            // 0=上传时新建并自动回写；已有则更新
  "project_id": 1,
  "intro": "世界简介（给玩家看）",
  "global_bg": "全局背景设定（写入 world settings.globalBackground）",
  "card_scenario": "角色卡场景设定（无则回退 global_bg）",
  "card_tags": ["Roleplay", "都市", "悬疑"],
  "avatars_subdir": "",     // 空=用 avatars/ 根；否则 avatars/<subdir>/
  "player_role": { "name": "陈曦", "md_file": "用户.md", "avatar_file": "用户.png" },
  "npc_roles": [
    { "name": "张晚意", "md_file": "张晚意.md", "avatar_file": "张晚意.png" }
  ],
  "chapter_covers": {
    "1": { "background": "chapter_1_bg.png" },
    "2": { "background": "chapter_2_bg.png" }
  }
}
```

**关键规则**
- `player_role` 取 `roles/用户.md`；其余 NPC 进 `npc_roles`
- `avatar_file` 必须对应 `avatars/` 下已存在的 PNG（生成头像是另一技能的事）
- `chapter_covers` 的 key 是章节序号字符串；`background` 文件名要匹配 `image/` 下实际文件
- 通用角色（某女子/某男子）也进 `npc_roles`，其 PNG 通常已存在

---

## 2. 章节 chapter_N.json + chapter_N_标题.md（JSON 优先配对）

位置：`{故事目录}/chapters/`。`chapters.py` 用 `_find_chapter_files`：
**同名 stem 时 JSON 覆盖 MD；数字前缀（chapter_1）覆盖无前缀文件**。

**JSON 字段契约**（7 字段，缺一不可）：

```json
{
  "title": "消失的同桌",
  "sort": 0,                       // 章节序号，去重用 sort 而非标题
  "openingRole": "旁白",           // 开场发言角色；自由章节可 null
  "openingText": "开场白……",       // 与 openingRole 对应
  "completionCondition": "成功条件（足够复杂，放末尾）",
  "backgroundPrompt": "章节背景图生图提示词",
  "content": "## 大阶段1\n### 小事件\n@旁白：…\n@角色：台词\n### 用户发言\n"
}
```

**关键规则（对齐 toonflow-chapter-design 技能）**
- `content` 必须与同名 `.md` **正文完全一致**（上传读 content；MD 仅作人读备份）
- **背景提示词**放 `backgroundPrompt`，MD 里**禁止写 `## 章节背景图` 块**（否则 md_parser 降级会把标题残留在 content 污染正文）
- **成功条件**放 `completionCondition`，MD 里**禁止写 `> 成功条件` 行**
- 旁白代称一律用"用户"，NPC 对玩家台词可用"你"
- 结构强制：`## 大阶段` + `### 小事件` + `### 用户发言`（每大阶段至少一次用户发言）
- `completionCondition` 要足够复杂，确保玩家体验完整章节才结束

---

## 3. 世界书 worldbook/worldbook.json

位置：`{故事目录}/worldbook/`。由 `worldbook_builder.build_worldbook` 从 MD 构建，再 `worldbook.py` 导入服务端。

**生成方式（推荐 MD → JSON）**：在 `worldbook/` 下按分类写 `.md`，再运行构建：

```bash
python -m src.cli toonflow worldbook-build --story "<故事名>"
# 或绕过故事解析直接给目录：
python -c "from src.toonflow.storyworld.worldbook_builder import build_and_save; build_and_save(r'ai_story/.../故事名')"
```

**分类 → category 映射**（`worldbook_builder.CATEGORY_MAP`）：

| 文件名 | category |
|--------|----------|
| `_constants.md` | worldConstants（主题/主角人设/风格） |
| `_system.md` | worldSystem（运行机制） |
| `world.md` | worldGeography |
| `locations.md` | worldLocations |
| `characters.md` | worldCharacters |
| `factions.md` | worldFactions |
| `items.md` | worldItems |
| `events.md` | worldEvents |
| `random.md` | worldRandom |
| `README.md` | （跳过，不解析） |

**单条 MD 格式**（每个 `## 标题` 是一条；文件头用纯文本，**不要**用 `>` 否则会被误判为条目）：

```
# 分类标题

本文件说明……（纯文本，无 > 行）

---

## 条目标题

- **Keys**: `["关键词1", "关键词2"]`
- **Constant**: `true`          # 常驻注入；非常驻可省略
- **Order**: `9001`             # 同分类内排序，越大越靠后
- **Content**:

> [条目标题] 正文第一段。
>
> - 列表项
> - 列表项
```

> ⚠️ **坑**：文件头若含 `>` 行，builder 会把文件头误判成一条 title 以 `#` 开头的垃圾条目。务必让文件头是纯文本。
> ⚠️ **坑**：条目 `Content` 必须非空，否则该条被跳过（`if not entry["content"].strip(): continue`）。

**构建产物结构**：`{ name, version, totalEntries, entries:[ {title,keys,constant,probability,order,category,content,...} ] }`，可被 `worldbook.py` 直接 import。

---

## 校验清单（交付前必跑）

```python
import json, pathlib
S = pathlib.Path(r"ai_story/.../故事名")
# story.json
sj = json.load(open(S/"story.json", encoding="utf-8"))
assert all(k in sj for k in ["story_name","world_id","project_id","intro","global_bg","card_scenario","card_tags","player_role","npc_roles","chapter_covers"])
# chapters
for n in [1,2]:
    j = json.load(open(S/"chapters"/f"chapter_{n}.json", encoding="utf-8"))
    md = (S/"chapters"/f"chapter_{n}.md").read_text(encoding="utf-8")
    assert all(k in j for k in ["title","sort","openingRole","openingText","completionCondition","backgroundPrompt","content"])
    assert j["content"] == md
    assert "## 章节背景图" not in md and "成功条件" not in md
# worldbook
wb = json.load(open(S/"worldbook"/"worldbook.json", encoding="utf-8"))
assert wb["totalEntries"] == len(wb["entries"])
assert all(e.get("content","").strip() for e in wb["entries"])
# 资源就位
for r in sj["npc_roles"] + [sj["player_role"]]:
    assert (S/"roles"/r["md_file"]).exists() and (S/"avatars"/r["avatar_file"]).exists()
for f in ["cover.png","chapter_1_bg.png","chapter_2_bg.png"]:
    assert (S/"image"/f).exists()
```

---

## 合格范例（黑塔：从超忆症开始成神）

- `story.json`：12 个 npc_roles（含某女子/某男子），chapter_covers 含 1/2
- `chapters/chapter_1.json` + `chapter_1.md`：主线，content==md，背景/成功条件已进 JSON
- `chapters/chapter_2.json` + `chapter_2.md`：自由章节，openingRole=null
- `worldbook/`：9 个分类 MD → 构建出 `worldbook.json` 共 **35 条**（worldConstants 3 / worldSystem 4 / worldGeography 2 / worldLocations 4 / worldCharacters 11 / worldFactions 3 / worldItems 3 / worldEvents 3 / worldRandom 2）
- 校验：`python -m src.cli toonflow worldbook --story 黑塔：从超忆症开始成神 --op import` 即可上传世界书

---

## 工作流（一句话）

读故事 canon（STORY.md / roles / chapters / 已有配置）→ 写 story.json → 写 chapter_N.json（背景/成功条件进 JSON，清理 MD）→ 写 worldbook/*.md 并 build → 跑校验清单 → 提示用户执行 `toonflow update` 与 `toonflow worldbook --op import`。
