# Toonflow 角色管理规则

## 环境配置
- local 环境: `http://localhost:60002`, worldId=35 (我的诡异表妹)
- 生产环境: `http://122.51.232.171:60002`

## 工作路径
- `work_in_path=ai_story/local` 指向本地环境工作目录
- 故事路径: `ai_story/local/故事名/`

## 配置规范（重要！）
- **全局 .env**: 项目根目录，包含 BASE_URL/TOKEN/账号等
- **故事级 .env 已废弃**: 不再需要！所有故事配置统一放 `story.json`
- **story.json 字段**: story_name, world_id(运行后自动回写), project_id, intro, global_bg, card_scenario, card_tags, avatars_subdir, player_role, npc_roles, chapter_covers
- **禁止硬编码**: 所有 ID、URL、TOKEN 必须从全局 .env 读取
- **WORLD_ID 自动保存**: 创建新世界后，脚本自动将 world_id 写回 story.json

## 必须排除的文件
1. `role.list.md` - 角色目录文档，不是角色文件
2. 任何不含 `raw_setting` 字段的 `.md` 文件

## playerRole vs NPC
- `用户.md` = playerRole（玩家角色）→ 设置到 `playerRole` 字段
- NPC = 设置到 `settings.roles` 数组

## 更新原则
- 已有角色 → 修改（更新字段）
- 无新角色需求 → 不新增

## worldId 传递
- saveWorld 必须包含 worldId

## 头像分离 API 用法
- 接口: POST `/game/separateRoleAvatar`
- 参数: `worldId`, `base64Data`, `roleName`
- 返回: `sourceFilePath`, `foregroundFilePath`, `backgroundFilePath`

## 音色生成
- 音色提示词（voicePromptText）仍然写入角色数据
- 音色文件由用户手动生成，脚本不自动调用 generateBindingVoice

## 封面图片上传
- `/game/uploadImage` 接口上传，返回 `filePath` 和 `path`
- 世界封面设置到 `coverPath` 和 `settings.coverPath`
- 章节封面/背景设置到 `settings.chapterExtras[]` 的 `coverPath`/`background`
- **章节背景图由 covers.py 统一管理**，chapters.py 只上传章节封面图，避免重复上传

## 章节去重规则
- 章节按 `sort` 序号匹配服务器现有章节（不是标题）
- 改标题不会导致重复创建
- 降级策略：sort 匹配不到时，尝试 title 匹配

## 完整更新脚本
- 位置: `src/toonflow/full_update.py`
- 功能: playerRole + NPC角色 + 章节 + 封面背景图 一体化更新
- CLI: `python -m src.cli toonflow update --story 故事名`

## 章节成功条件设计原则
- 成功条件要放在章节**末尾**，不能放在中间
- 条件要足够复杂，确保玩家体验完整章节后才结束
- 例如：第一章"与顾家人完成初次见面"太简单，应放在夜谈之后

## 章节结构规范（chapter-writing-guide.md）

### 结构层级
```
## 大阶段（大事件）
### 小事件1
@旁白：描述场景/动作（不要替用户说话）
@角色名：台词
### 用户发言          ← 每个大阶段至少一次用户发言
### 小事件2
### 用户发言
### 小事件3
### 用户发言
## 大阶段2
### 小事件1
### 用户发言
...
```

### 核心规则
1. **不要全是 `###`，必须有 `##` 大阶段**
2. **每个大阶段里，用户至少发言一次**：`### 用户发言` 块
3. **旁白不要帮用户说话**：旁白只描述场景/NPC动作，不写用户的决定/感受/台词
4. **用户发言留给玩家**：用 `### 用户发言` 让玩家自己说
5. **事件篇幅**：推荐三个台词一个小事件，三小事件组成大事件，小事件不要过长
6. **这可交互AI故事，不是小说**：玩家的选择和发言是核心

### 示例模板
```markdown
## 回乡

### 站台
@旁白：用户本以为这只是一次普通的回乡探亲...
@小七：表哥，欢迎回来。走吧，我先带你去学校报到。
### 用户发言
> 用户可以选择回应方式

### 深入了解
@旁白：小七笑着拉住用户的袖子...
@小七：对了，表哥，你知道苏老师吗？
### 用户发言
```


## 世界书构建工具（2026-07-28）
- 位置: `src/toonflow/storyworld/worldbook_builder.py`
- CLI: `python -m src.cli toonflow worldbook-build --story 故事名`
- 功能: 把 `ai_story/local/故事名/worldbook/*.md` 解析为 `worldbook.json`
- 上传: `python -m src.cli toonflow worldbook --story 故事名 --op import`
- 世界书 MD 文件格式: `## 标题` + `- **Keys**: \`["k1"]\`` + `- **Content**:` + `> 正文`
- 当前谁让这个山大王修仙的(worldId=41): 96条条目，13个分类

## 通用代码库 src/（2026-07-16 重构）
- 位置: src/
- CLI: python -m src.cli
- story.json 配置文件替代硬编码
- 详见 .workbuddy/memory/2026-07-16.md
