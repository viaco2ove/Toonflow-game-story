# Worldbook 说明

## 什么是 Worldbook？
Worldbook 是 Toonflow 互动故事系统的世界知识库，提供角色设定、世界观、规则说明，供 AI 在生成剧情时参考。

## 文件结构
- `worldbook.json` —— 角色与世界观条目（JSON，AI 直接读取）
- `_system.md` —— 系统级设定（三大机制、喜剧铁律、修为等级）
- `_constants.md` —— 常量（角色阵容、修为等级、核心地点）
- `characters.md` —— 角色速查表
- `world.md` —— 世界观设定

## 编辑规范
- `worldbook.json` 中的 `constant: true` 条目为全局常量，优先级最高
- `keys` 数组内的关键词触发对应条目
- 万能角色（某男子/某女子）必须带「饰演xxx」前缀才能使用
- 编辑后验证 JSON 语法：`python -c "import json; json.load(open('worldbook.json'))"`
