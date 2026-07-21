# 自由模式编排 + 世界书接入方案

> 解决问题：自由模式下"没有事件了"如何编排；SillyTavern 世界书机制能否接入；如何让自由模式更鲜活、更有世界感。

---

## 一、当前自由模式的编排机制（已实现）

### 1.1 判定入口

后端 `src/lib/gameEngine.ts:1145` 的 `isFreeChapterRuntimeMode(chapter)`：

```ts
return !hasCompletionCondition && !hasEndingRules;
```

章节没有 `completionCondition`、`runtimeOutline.endingRules` 都为空 → 自动进入自由模式。

### 1.2 双轨运行时

| 阶段 | 触发条件 | 实现位置 |
|------|----------|----------|
| 静态 phase 推进 | runtimeOutline.phases 还没全部完成 | `ChapterProgressEngine.ts` |
| 动态事件 free_runtime | 静态 phase 全完成（`areAllFreeChapterStaticPhasesCompleted`） | `ensureFreeChapterDynamicEventState` |

### 1.3 任务驱动循环（核心）

`FreeChapterTaskService.ts` 实现：

```
玩家："给我推荐个任务"
  ↓
旁白：从 ## 非事件: 任务分类 块抽 5 个，列给玩家
  ↓
玩家："选 3"
  ↓
AI 生成 FreeChapterTaskBlueprint：
  { taskTitle, objective, process[], successConditions[], failureConditions[], eventFacts[] }
  ↓
写入 vars.activeFreeTask → 变成动态事件
  ↓
任务完成 → 清空 activeFreeTask → 回到推荐循环
```

### 1.4 章节内容里"非事件"块的真实作用

源码 `gameEngine.ts:438`：

```ts
function isNonEventHeading(input: string): boolean {
  return /^非事件(?:\s*[:：].*)?$/u.test(heading);
}
```

`## 非事件:` 块被识别后：
- **不参与** phase 生成、不进入事件推进链
- **作为上下文**提供给旁白 AI
- 当前主要用来放"任务分类列表"

> **关键发现**：这个块本质上已经是"低配版世界书"——给 AI 提供背景知识，但目前是**静态全注入**，没有触发式激活能力。

---

## 二、SillyTavern 世界书机制

### 2.1 核心模型

世界书 = 一本"会自己翻页的词典"：每条记录有 `keys`（触发词）和 `content`（注入正文），AI 聊到相关话题时自动激活对应词条。

### 2.2 词条字段（V2 规范）

```json
{
  "keys": ["苏老师", "数学课"],
  "secondary_keys": ["办公室"],
  "selective": true,
  "selective_logic": "AND",
  "content": "苏老师深夜在办公室批改试卷，但其实她...",
  "constant": false,
  "position": "before_char",
  "insertion_order": 100,
  "depth": 4,
  "probability": 100,
  "enabled": true,
  "case_sensitive": false,
  "extensions": {}
}
```

### 2.3 四种触发模式

| 模式 | 字段 | 行为 |
|------|------|------|
| 关键词触发 | `keys` + 默认 | scan_depth 范围内扫对话，命中即激活 |
| 选择性触发 | `selective:true` + `secondary_keys` | 主键 AND/NOT 次键的逻辑组合 |
| 常驻 | `constant:true` | 在 token 预算内始终注入 |
| 概率 | `probability:N` | 命中后按概率决定是否真注入 |

### 2.4 注入位置

- `before_char`：角色定义之前（最常用于世界观）
- `after_char`：角色定义之后
- `@depth=N`：注入到对话历史第 N 条之后（深度注入，影响"近期上下文"）

### 2.5 预算与递归

- `token_budget`：所有词条总 token 上限，超出按 `priority` 丢弃
- `recursive_scanning`：词条 A 的内容命中词条 B 的 key，链式激活 B

### 2.6 关键差异

| 维度 | Toonflow 自由模式 | SillyTavern 世界书 |
|------|-------------------|---------------------|
| 触发模型 | 任务驱动（玩家主动要任务） | 关键词驱动（对话自动激活） |
| 注入方式 | 旁白 prompt 中静态全注入 | prompt 构造时动态拼装 |
| 状态管理 | vars.activeFreeTask | 词条 enabled + 预算控制 |
| 编辑入口 | 章节 MD 的 `## 非事件:` | ST 前端 lorebook 编辑器 |
| 是否可后端消费 | 是（后端原生支持） | 否（仅 ST 前端消费） |

> **结论**：两者正交。Toonflow 的"任务流"和 ST 的"关键词触发"可以共存互补。

---

## 三、接入方案（按改动量分级）

### 方案 A · 轻量级：扩展 `## 非事件:` 语法

**改动量**：0 后端代码，只改章节 MD 写法 + 旁白 prompt 指令。

**章节 MD 新语法**：

```markdown
## 非事件: 苏老师真相 [trigger: 苏老师, 数学课, 办公室, 钢琴声]

苏老师并非普通教师，她是校长用来"筛选"学生的诡异存在。
她白天温文尔雅，深夜在办公室批改试卷时会哼出诡异曲调，
凡是被她叫去办公室的学生，都会在第二天"转学"。
她与小七有某种隐秘的协议——小七保护的用户，她不会动手。

## 非事件: 学校规则 [trigger: 宿舍, 十点, 脚步声, 走廊, 开门] [constant]

晚上十点之后不能离开宿舍。
听到走廊脚步声不能开门。
不要试图离开学校。
这些规则的真正含义是：夜间的学校会进入"诡异时间"，
所有没有"庇护"的人类都会被吞噬。

## 非事件: 玩家阵营 [trigger: 阵营, 人类, 诡异, 抉择, 投靠]

玩家在故事中可能选择的阵营：
- 人类学生阵营：与李明、王思远等人类学生结盟
- 诡异阵营：被小七或校长收编
- 中立阵营：游走在两方之间
选择阵营后，旁白应通过 @记忆管理 写入玩家角色卡的 other 字段。
```

**旁白 prompt 指令补充**（加到 `initDB.prompts.ts` 的旁白系统提示词）：

```
你在自由模式下需要遵循"世界书激活原则"：
1. 章节中的"## 非事件: 名称 [trigger: 关键词]"块是世界书词条
2. 当玩家对话内容命中某词条的 trigger 关键词时，将该词条的内容纳入本次编排的上下文
3. 标记为 [constant] 的词条始终纳入上下文，无需关键词触发
4. 同时激活的词条过多时，优先保留与当前对话最相关的 3-5 条
5. 词条内容是"世界设定"而非"事件指令"，不要把词条当成剧情直接发生
```

**优点**：
- 立即可用，不改一行后端代码
- 写作体验与现有 `## 非事件: 任务分类` 完全一致，只是多了 trigger 标记
- AI 自然语言能理解"激活"语义

**局限**：
- 靠 AI 自觉执行激活，没有强约束
- 没有 token 预算控制（但 Toonflow 后端本身就有上下文管理）
- 没有概率/递归触发

### 方案 B · 中量级：填充 `character_book` 字段

**改动量**：动 `src/cards/builder.py` 和角色 MD 模板。

**角色 MD 新增段**：

```markdown
## 世界书
- keys: ["黑色发卡", "诡异发卡"]
  content: "黑色发卡是小七压制自身诡异气息的道具，
           一旦摘下，她的冥尊级力量会无差别压制周围一切存在"
  constant: false

- keys: ["影子", "分裂"]
  content: "小七的影子永远分裂为两道，边缘有黑雾缭绕，
           这是她上位诡异身份的标志，普通人看不见"
  constant: false

- keys: ["表妹", "真正的表妹"]
  content: "小七与用户真正的表妹关系未知，
           她选择以表妹身份保护用户，原因成谜"
  constant: false
```

**builder.py 改造**：

```python
# src/cards/builder.py - build_v2_card 函数内
character_book = parse_worldbook_from_md(role_md_path)  # 新增解析函数

v2_card = {
    "spec": "chara_card_v2",
    "data": {
        ...
        "character_book": character_book,  # 替换原来的 None
        ...
    }
}
```

**优点**：
- SillyTavern V2 规范原生支持，导出即可用
- chub.ai / cards.sillytavern.one 上传后 ST 端能直接享受世界书
- 角色卡自带"角色级"世界设定，迁移性强

**局限**：
- Toonflow 后端不消费 `character_book` 字段（它有自己的角色 + 章节体系）
- 只影响导出的角色卡，对 Toonflow 内运行时无影响
- 角色级世界书 vs 世界级世界书：ST 还有独立的 `World Info` 不绑角色

### 方案 C · 重量级：Toonflow 后端实现世界书

**改动量**：动数据库表 + API + Prompt 引擎。

**数据库**：

```sql
CREATE TABLE world_info_entries (
  id INTEGER PRIMARY KEY,
  worldId INTEGER NOT NULL,
  chapterId INTEGER,           -- NULL=世界级，非 NULL=章节级
  keys TEXT NOT NULL,          -- JSON 数组
  secondary_keys TEXT,
  content TEXT NOT NULL,
  selective INTEGER DEFAULT 0,
  selective_logic TEXT,
  constant INTEGER DEFAULT 0,
  position TEXT DEFAULT 'before_char',
  insertion_order INTEGER DEFAULT 100,
  depth INTEGER,
  probability INTEGER DEFAULT 100,
  enabled INTEGER DEFAULT 1,
  comment TEXT,
  sort INTEGER DEFAULT 0
);
```

**新增 API**：
- `POST /game/saveWorldInfo` - 创建/更新词条
- `POST /game/listWorldInfo` - 列出词条
- `POST /game/deleteWorldInfo` - 删除词条

**NarrativeOrchestrator 改造**：

```ts
// 构造 prompt 前
const activeEntries = scanAndActivateWorldInfo({
  worldId: chapter.worldId,
  chapterId: chapter.id,
  recentMessages: state.messages.slice(-scanDepth),
  tokenBudget: 2000,
});
const worldInfoBlock = activeEntries
  .sort((a, b) => a.insertion_order - b.insertion_order)
  .map(e => `[${e.comment || e.keys[0]}]\n${e.content}`)
  .join('\n\n');
// 注入到 system prompt 的指定位置
```

**优点**：
- 完整 ST 等价能力，包括预算、概率、递归
- 可视化编辑器可加到 Toonflow 后台
- 与现有任务系统并行，自由模式更丰富

**局限**：
- 改动量大（新增表 + API + Prompt 引擎改造 + 前端编辑器）
- 需要后端发版
- 短期看不到收益

### 推荐路径

**先 A → 验证玩法 → 再 B → 玩法固化后 C**：

1. **现在（1-2 天）**：方案 A，扩展章节 MD 语法，写 10-20 个关键词条
2. **2 周内**：方案 B，让导出的角色卡自带世界书（不增加 Toonflow 运行时负担）
3. **1 个月后**：评估是否需要方案 C（取决于 A+B 的实际效果）

---

## 四、让自由模式更鲜活的 6 条具体建议

### 4.1 建立"动态事件库"（不只是任务）

当前 `## 非事件: 任务分类` 只有任务。建议扩展为多类事件：

```markdown
## 非事件: 突发事件池 [trigger: 自由, 探索, 走动]

- 浓雾突然加重，能见度不足三米
- 校园广播响起，播报一则五年前的旧新闻
- 操场出现一群学生在做早操，但他们都面无表情
- 食堂今天供应的菜里混着不该出现的东西
- 图书馆的某本书自己从书架上掉下来
```

旁白在玩家"自由探索"时随机抽 1 个，让世界自己"动起来"。

### 4.2 NPC 关系网动态化

```markdown
## 非事件: NPC 关系网 [trigger: 关系, 好感, 信任, 阵营] [constant]

- 小七 ↔ 校长：表面服从，暗中对抗
- 小七 ↔ 苏老师：互不干涉，但都有底线
- 校长 ↔ 苏老师：合作筛选学生
- 李明 ↔ 王思远：人类学生中的领袖，互相防备
- 玩家与 NPC 的好感度变化时，旁白应通过 @记忆管理 更新关系
```

### 4.3 时间/天气系统

```markdown
## 非事件: 时间系统 [trigger: 时间, 早晨, 中午, 黄昏, 夜晚, 十点] [constant]

游戏内时间分为五个时段，每个时段触发不同事件概率：
- 早晨（6-10）：人类学生活跃，诡异沉睡
- 中午（10-14）：相对安全，适合调查
- 黄昏（14-18）：诡异开始苏醒，影子分裂可见
- 夜晚（18-22）：诡异活跃，但仍在规则内
- 深夜（22-6）：诡异时间，规则失效，禁止外出

旁白应通过 @记忆管理 跟踪当前时段，并在编排时反映时段特征。
```

### 4.4 隐藏触发与彩蛋

```markdown
## 非事件: 隐藏剧情触发 [trigger: 三楼, 厕所, 第三格, 镜子]

如果玩家在深夜 11 点之后进入三楼厕所第三格照镜子，
并且身上带着小七的玉片，将触发"镜像世界"隐藏剧情。
旁白应主动描述镜子里的异象，引导玩家发现。
此剧情只能触发一次，触发后写入 @记忆管理 的 other 字段。
```

### 4.5 任务前缀分级（区分剧情/支线/日常）

```markdown
## 非事件: 任务分类（带分级）

### 剧情类 [main]
- 发现小七的真实身份
- 揭开学校的秘密
- 找到离开的方法

### 支线类 [side]
- 寻找失踪的同学
- 校长的邀请函
- 半夜的钢琴声

### 日常类 [daily]
- 收集止血草
- 修复破损装备
- 维持体力与状态
```

旁白推荐时按"剧情 30% / 支线 50% / 日常 20%"配比，避免玩家被一堆日常任务淹没。

### 4.6 玩家选择的"蝴蝶效应"记录

```markdown
## 非事件: 玩家选择追踪 [trigger: 选择, 抉择, 决定] [constant]

旁白应记录玩家的关键选择，并在后续编排中体现后果：
- 是否接受小七的玉片 → 影响后续小七的态度
- 是否在十点前回宿舍 → 影响遭遇诡异的事件
- 是否与李明结盟 → 影响人类学生阵营的态度
- 是否调查苏老师 → 影响苏老师是否动手

每次玩家做出选择，旁白通过 @记忆管理 写入"决定_X"标记到 other 字段。
后续编排时读取这些标记，让 NPC 反应符合玩家过往选择。
```

---

## 五、立即可做的最小改动（1 小时内见效）

### 步骤 1：在 `我的诡异表妹` 第 1 章追加 5-10 个世界书块

打开 `ai_story/local/我的诡异表妹/chapters/chapter_1.md`，在 `## 非事件: 任务分类` 之后追加：

```markdown
## 非事件: 学校三大诡异 [trigger: 三大诡异, 上位诡异, 校长, 苏老师, 小七] [constant]

学校三大上位诡异：
1. 校长 - 诡帝级，掌控整个学校
2. 苏老师 - 邪宗级，负责筛选学生
3. 小七 - 冥尊级，保护用户的存在
三者互不干涉，但都有各自的"领地"。

## 非事件: 玉片的功能 [trigger: 玉片, 护身符, 捏碎]

小七给的玉片是冥尊级诡异道具：
- 平时被动防护，可抵御一次致命攻击
- 主动捏碎可释放小七的一道分身
- 用完后会变成普通石头，需要小七重新注入力量

## 非事件: 学校禁区 [trigger: 禁区, 三楼, 图书馆, 校医院]

学校有三个禁区：
1. 三楼厕所第三格 - 镜像世界入口
2. 图书馆禁书区 - 藏有诡异契约
3. 校医院深夜急诊 - 诡异改造室
进入禁区需要满足特定条件，否则会被传送回宿舍。
```

### 步骤 2：调用 `python -m src.cli toonflow update --story 我的诡异表妹` 推送更新

### 步骤 3：在新会话中测试

- 玩家提到"苏老师"时，旁白应主动调用"学校三大诡异"块的内容
- 玩家进入三楼时，旁白应主动调用"学校禁区"块的内容
- 如果不奏效，加强旁白 prompt 指令（方案 A 的步骤 2）

---

## 六、参考资料

- **Toonflow 后端源码**：`D:\Users\viaco\tools\Toonflow-game\toonflow-game-app\src\`
  - `lib/gameEngine.ts:1145` - `isFreeChapterRuntimeMode`
  - `modules/game-runtime/engines/ChapterProgressEngine.ts:574` - `ensureFreeChapterDynamicEventState`
  - `modules/game-runtime/services/FreeChapterTaskService.ts` - 任务推荐循环
- **角色卡构建器**：`src/cards/builder.py:105` - `character_book: None` 待填充
- **SillyTavern V2 规范**：https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md
- **ST 世界书实用指南**：https://sillycard.xyz/zh/blog/st-fields-04-character-book
- **当前项目角色 MD 示例**：`ai_story_exsample/local/我的诡异表妹/roles/小七.md`
- **自由章节示例**：`ai_story_exsample/local/我的诡异表妹/chapters/chapter_1.md`
