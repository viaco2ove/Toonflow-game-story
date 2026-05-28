# Toonflow 角色·故事·章节 设计概要

> 学习自 `toonflow-game-app` 项目文档，2026-05-16

---

## 一、角色设计

### 1.1 万能角色

在角色设定中标注 `万能角色`，该角色可扮演各种野怪、NPC，用于丰富剧情。

- **不分性别的万能角色**：`路人甲`、`万能角色`。若未创建万能角色，旁白本身就是一个特殊的万能角色。
- **区分性别的万能角色**：`某男士`、`某女士`

万能角色可以用 `(扮演xxx)` 形式扮演特定人物，例如：
```
路人甲：（扮演唐三藏）徒儿你不要杀生
```

### 1.2 角色参数卡

角色参数卡是游玩过程中动态存储的角色数据，从角色描述通过 AI 自动提取。

**基础字段**：
- `name` - 角色名
- `raw_setting` - 原始角色设定
- `gender` - 性别
- `age` - 年龄
- `personality` - 性格
- `appearance` - 外貌
- `voice` - 音色特点
- `skills` - 技能列表
- `items` - 物品列表
- `equipment` - 装备列表
- `level` - 等级
- `level_desc` - 等级称号（如"斗之气 1星"）
- `hp` - 血量
- `mp` - 蓝量
- `money` - 金钱
- `other` - 其他动态参数

**JSON 格式示例**：
```json
{
  "name": "孙悟空",
  "raw_setting": "花果山水帘洞美猴王...",
  "gender": "男",
  "level": 1,
  "level_desc": "斗之气 1星",
  "age": null,
  "personality": "豪爽、好战",
  "appearance": "毛脸雷公嘴",
  "voice": "粗犷有力",
  "skills": ["七十二变", "筋斗云"],
  "items": [],
  "equipment": ["如意金箍棒"],
  "hp": 100,
  "mp": 0,
  "money": 0,
  "other": []
}
```

---

## 二、故事模式

### 2.1 三种游玩模式

| 模式 | 说明 | 入口 |
|------|------|------|
| **调试 (debug)** | 故事编辑时对某一章节进行调试，不产生"聊过"记录，不持久化动态数据。点击调试按钮时先自动保存内容。没有下一章节时结束显示"已完结"或"已失败"。 | 每个章节-调试按钮 |
| **游玩 (play)** | 用户发送内容才会成为"聊过"记录。动态数据持久化，续聊时加载。不影响故事静态数据。 | 主页/聊过-续聊/我的 |
| **观看 (watch)** | 像看电影一样观看台词播放（可有声/无声），有进度条可前后拖动，无用户输入框。可修改/删除某个台词。 | 聊过-观看 |

### 2.2 游玩流程（调试/游玩通用）

1. 保存草稿 → 进入调试界面 → 创建会话环境 → 读取记忆 → 准备剧情编排完毕
2. 前端发送编排请求 → 剧情编排 → 流式输出角色台词（可选语音）→ 播放完毕
3. 编排通知前端到达用户发言节点 → 用户输入内容或语音
4. 过程中检查成功条件（章节结局）、修改游戏/角色参数、记忆管理师后台工作

### 2.3 角色发言规则

- 轮到用户发言时，用户不能输入则发送 `.` 跳过
- `（...）`、`[...]` 小挂号和中挂号内的内容是特殊内容，文字转语音时不读出
- 特殊内容示例：好感度变化、血量蓝量变化、内心想法等

---

## 三、章节设计

### 3.1 章节内容结构

章节内容使用 **Markdown 格式**，通过 `##` 二级标题划分不同阶段（Phase）。

**示例**：
```markdown
## 全局状态（仅用户可见）
@系统：你已被卷入【混沌裂隙】...

## 场景开始
@旁白：破碎的星辰残骸漂浮在虚空之中...

## 🧩 用户行动1（被编排触发）
@系统（仅对用户）：你被冲击波掀飞...

## 主线推进
@旁白：战斗愈发激烈...

## 非事件：时间停滞
@旁白：爆炸达到顶点...
```

### 3.2 Phase（阶段）对象

每个 `##` 标题下的内容为一个 Phase，编译为结构化对象：

```typescript
interface ChapterRuntimePhase {
  id: string;                      // 如 "phase_1_全局状态"
  label: string;                   // 如 "全局状态（仅用户可见）"
  kind: "opening" | "scene" | "user" | "fixed";  // 阶段类型
  targetSummary: string;           // 阶段目标摘要
  userNodeId: string | null;       // 用户节点ID（如果是用户行动阶段）
  allowedSpeakers: string[];       // 允许发言的角色列表
  nextPhaseIds: string[];          // 下一个阶段的候选ID列表
  defaultNextPhaseId: string | null;
  requiredEventIds: string[];      // 前置要求事件ID
  completionEventIds: string[];   // 完成时触发的事件ID
  advanceSignals: string[];        // 推进信号
  relatedFixedEventIds: string[];  // 关联的固定事件ID
}
```

### 3.3 章节结构化模板

每个章节可编译为结构化运行模板：

```json
{
  "chapterId": 14,
  "title": "第 2 章",
  "opening": [
    { "role": "旁白", "type": "narrator", "content": "混沌虚空之中..." }
  ],
  "phases": [
    {
      "id": "phase_1_battle_start",
      "label": "双悟空交战",
      "mustEvents": ["goku_enter", "battle_started"],
      "allowedSpeakers": ["旁白", "西游孙悟空", "龙珠孙悟空"],
      "targetSummary": "建立混沌战场与初始冲突"
    },
    {
      "id": "phase_2_user_observe",
      "label": "用户行动1",
      "userNodeId": "user_turn_1",
      "allowedSpeakers": ["旁白", "系统"],
      "targetSummary": "把用户推到混沌晶石互动点"
    }
  ],
  "userNodes": [
    {
      "id": "user_turn_1",
      "promptRole": "系统",
      "goal": "让用户围绕混沌晶石作出第一次行动",
      "suggestions": ["观察", "接触晶石", "接近战场", "提醒某人"],
      "minInputs": 1
    }
  ],
  "fixedEvents": [
    {
      "id": "xuyang_steals_staff",
      "label": "徐阳偷走如意金箍棒",
      "requiredBeforeFinish": true
    }
  ],
  "endingRules": {
    "success": ["xuyang_steals_staff"],
    "failure": [],
    "nextChapterId": 15
  }
}
```

### 3.4 章节推进状态

会话运行态维护 `chapterProgress`：

```json
{
  "chapterProgress": {
    "phaseId": "phase_2_user_observe",
    "phaseIndex": 1,
    "userNodeId": "user_turn_1",
    "userNodeStatus": "waiting_input",
    "completedEvents": ["goku_enter", "battle_started"],
    "pendingGoal": "让用户围绕混沌晶石作出第一次行动",
    "fixedOutcomeLocked": false
  }
}
```

### 3.5 章节判定器

独立的章节判定器负责判断章节是否成功/失败/继续：

```json
{
  "result": "continue",
  "matched_rule": null,
  "reason": "用户尚未输入名称、性别、年龄，未满足结束条件",
  "next_chapter_id": null,
  "guide_summary": "需要引导用户输入角色名称、性别和年龄",
  "guide_facts": ["用户尚未提供角色基本信息", "需要询问用户角色名称", "需要询问用户角色性别和年龄"]
}
```

`result` 可选值：`continue` / `success` / `failed`

### 3.6 自由章节

**简单自由章节**：无章节内容、无结束条件，角色与用户自由聊天。

**复杂自由章节**：可设计任务推荐系统，例如旁白角色不断随机推荐5个任务（生存类/成长类/探索类/交互类/对抗类/机缘类/阵营类/隐藏类），用户选择后进入任务。

---

## 四、编排师 2.0 核心设计

编排师 2.0 的核心是**职责拆分**：

| 职责 | 负责方 |
|------|--------|
| 这一小步谁说话、为什么说 | **编排师** |
| 把"角色+动机"写成台词 | **发言器** |
| 是否满足成功/失败/下一章条件 | **章节判定器** |
| 当前阶段允许发生什么 | **状态机** |

编排师只输出：
```json
{
  "speaker": "旁白",
  "roleType": "narrator",
  "motive": "把用户推到混沌晶石互动点",
  "awaitUser": false,
  "nextRole": "系统",
  "nextRoleType": "system"
}
```

编排师**不再负责**：
- 章节阶段推进
- 章节成功/失败判定
- 固定结局是否发生
- 下一章节 ID

---

## 五、参考文档路径

- 角色设计：`md/plan/ai_game/V3/游玩业务/V1_V2/万能角色设计.md`
- 章节设计：`md/plan/ai_game/V3/章节设计/章节的事件列表设计.md`
- 编排师 2.0：`md/plan/ai_game/V3/游玩业务/V1_V2/编排师_2_0.md`
- 自由章节：`md/plan/ai_game/V3/游玩业务/V1_V2/自由章节设计.md`
- 角色参数：`md/plan/ai_game/V3/角色参数设计.md`
- 故事模式：`md/plan/ai_game/V3/游玩业务/V1_V2/故事模式和章节结束条件设计（调试）.md`