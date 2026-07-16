# Toonflow 角色管理规则

## 环境配置
- local 环境: `http://localhost:60002`, worldId=35 (我的诡异表妹)
- 生产环境: `http://122.51.232.171:60002`

## 工作路径
- `work_in_path=ai_story/local` 指向本地环境工作目录
- 故事路径: `ai_story/local/故事名/`

## .env 配置规范（重要！）
- **位置**: 每个故事根目录下的 `.env` 文件（不是 python/ 目录）
- **禁止硬编码**: 所有 ID（WORLD_ID、PROJECT_ID）、URL、TOKEN 必须从 .env 读取
- **自动保存**: 创建新世界后，脚本自动将 WORLD_ID 写回 .env
- **脚本路径**: `ai_story/local/故事名/python/full_update.py`
- **.env 字段**:
  - `BASE_URL`: 服务器地址
  - `TOKEN`: 认证令牌
  - `PROJECT_ID`: 项目ID
  - `WORLD_ID`: 世界ID（0=创建新世界，运行后自动更新）
  - `STORY_NAME/INTRO/GLOBAL_BG`: 故事基本信息
  - `ROLE_NAME_TO_FILE`: JSON，角色名→MD文件映射
  - `ROLE_NAME_TO_AVATAR`: JSON，角色名→头像文件映射

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
- 脚本位置: `ai_story/local/故事名/python/upload_covers_local.py`
- `/game/uploadImage` 接口上传，返回 `filePath` 和 `path`
- 世界封面设置到 `coverPath` 和 `settings.coverPath`
- 章节封面/背景设置到 `settings.chapterExtras[]` 的 `coverPath`/`background`

## 完整更新脚本
- 位置: `ai_story/local/故事名/python/full_update_correct.py`
- 功能: playerRole + NPC角色 + 章节 + 封面背景图 一体化更新
- BASE_DIR 必须是 Windows 绝对路径: `D:/Users/...`

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
