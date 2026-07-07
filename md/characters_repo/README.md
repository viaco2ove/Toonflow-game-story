# 角色卡仓库维护文档

## 目录结构

```
D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story\
├── characters_repo\                          ← 角色卡源文件（PNG + JSON）
│   └── 破局-从冷落走到瞩目\
│       ├── INDEX.md                          ← 使用指南
│       ├── 旁白-叙事者.png/json             ← 叙事者角色卡
│       ├── 世界书.json                       ← SillyTavern 世界书
│       ├── 顾泽.png/json                     ← 玩家角色
│       ├── 顾子航.png/json                   ← 核心反派
│       └── ...（其他 NPC）
│
└── md\characters_repo\                       ← 维护文档
    ├── README.md                             ← 本文档
    ├── upload_guide.md                       ← 上传指南
    └── build_guide.md                        ← 构建脚本说明
```

## 角色卡仓库配置

`.env` 中定义：
```env
characters_repo=https://cards.sillytavern.one/
characters_repo_local=D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story\characters_repo
characters_username=***REMOVED***
characters_password=***REMOVED***
```

## 当前支持的上传平台

| 平台 | 地址 | 上传方式 | 状态 |
|------|------|----------|------|
| cards.sillytavern.one | cards.sillytavern.one | 运营方收录，无公开 API | ⚠️ 需联系运营 |
| Chub.ai | chub.ai | 网页手动上传，无公开 API | ⚠️ 需手动 |
| SillyTavern-Card | github.com/tolixing/SillyTavern-Card | Docker 自建，有 POST /api/upload | ✅ 推荐自建 |

## 平台详细说明

### cards.sillytavern.one
- **性质**：精选索引站，卡片由运营方手动收录
- **上传**：无公开上传入口，需联系运营方收录
- **无 API**：不支持批量上传

### Chub.ai
- **性质**：全球最大角色卡分享平台，百万级卡片
- **上传**：网页手动上传，无公开 API
- **上传路径**：登录后 → Create Character → 填写表单 → 上传 PNG
- **格式要求**：PNG（内嵌 V2 JSON）或纯 JSON
- **无 API**：不支持批量/程序化上传

### SillyTavern-Card（推荐自建）
```bash
# Docker 一键部署
git clone https://github.com/tolixing/SillyTavern-Card.git
cd SillyTavern-Card
docker compose up -d

# 上传 API
POST /api/upload
Content-Type: multipart/form-data
- file: PNG 文件
- name: 角色名称
- version: 版本号
- description: 描述
```

## 角色卡规范

- **格式**：SillyTavern V2 (`chara_card_v2`)
- **嵌入**：PNG tEXt chunk, keyword=`chara`, value=base64(UTF-8 JSON)
- **JSON 独立文件**：每个角色同时输出 PNG 和 JSON 两个版本
- **Toonflow 数据**：保存在 `extensions.toonflow` 字段

## 更新流程

当 Toonflow 故事的角色 MD 文件更新后：
1. 运行 `characters_repo/build_cards.py` 重新生成所有角色卡
2. 重新生成叙事者角色卡（`build_narrator_card.py`）
3. 手动上传到目标平台