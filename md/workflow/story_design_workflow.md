## 创作故事-风暴阶段
路径:{work_in_path}/{story_name}/res
res 文件下没有结构和形式的限制
这个文件夹不是最终产物而是中间产物
故事构思阶段的产出-》res 文件夹下
作用说明如下：
[res.md](../res.md)

## ai故事创建的预备
路径:{work_in_path}/{story_name} 
使用说明如下：
[story.md](../story.md)

目录结构较为固定，用于生成
{work_in_path}/{story_name}/story.json

## 故事的数据化阶段
生成{work_in_path}/{story_name}/story.json

## 故事的接口代码
架构
src/
├── config.py           (315行) 统一配置：全局 .env + 故事 .env + story.json
├── md_parser.py        (182行) MD 文件解析（角色、章节）
├── png_utils.py        (130行) PNG tEXt chunk 嵌入/验证（支持 JPEG→PNG）
├── cli.py              (133行) 统一命令行入口
├── toonflow/
│   ├── client.py       (232行) Toonflow API 客户端
│   ├── roles.py        (108行) 角色更新（玩家+NPC+头像分离）
│   ├── chapters.py      (137行) 章节更新（JSON/MD，按sort去重，只上传封面图）
│   ├── covers.py        (94行) 封面/背景图上传
│   └── full_update.py  (132行) 一键完整更新编排
└── cards/
    ├── builder.py      (257行) 角色卡构建（MD→V2 JSON+PNG）
    ├── chub_ai.py      (299行) chub.ai 上传
    └── sillytavern.py  (273行) cards.sillytavern.one 上传
每个故事只需一个 story.json
放在 {work_in_path}/{story_name}/story.json，包含角色映射、场景设定、标签等。
**不再需要故事级 .env**，所有配置（world_id, project_id, intro, global_bg 等）统一放 story.json。


CLI 用法
bash
```
# 列出所有故事
python -m src.cli list-stories

# Toonflow 故事更新（世界+角色+章节+封面）
python -m src.cli toonflow update --story 破局-从冷落走到瞩目

# 角色卡构建
python -m src.cli cards build --story 破局-从冷落走到瞩目
python -m src.cli cards build --story 我的诡异表妹 --output chub_ai

# 上传到 chub.ai
python -m src.cli cards chub --story 我的诡异表妹
python -m src.cli cards chub --story 我的诡异表妹 --name 许飞
python -m src.cli cards chub --story 我的诡异表妹 --avatar-only

# 上传到 cards.sillytavern.one
python -m src.cli cards sillytavern --story 破局-从冷落走到瞩目
```

## 故事的接口代码 流程
### 大概流程：
判定故事是否已经创建(story.json 中 world_id>0)->没有就先创建空的故事草稿->获取id->配置故事id(world_id 写回 story.json)->
保存故事的基本信息和角色信息-》上传头像-》创建或者更新故事章节（按 sort 序号匹配，改标题不会重复创建）-》上传封面和背景图
### 特别注意：
- 不要重复创建故事，要使用统一的故事id
- 章节按 sort 序号去重（不是标题），改标题不会导致重复创建
- 章节背景图由 covers.py 统一管理，chapters.py 只上传封面图，避免重复上传
- 每次对故事或者角色信息的修改，都需要跑一次 full_update 完整更新
