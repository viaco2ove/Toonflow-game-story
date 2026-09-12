# workflow 工作流规范

## 核心原则

**只允许通过 `--op` 入口函数操作，不允许直接调用 `save_chapter_entry` / `get_chapter_entry` 等内部函数。**

所有对 Toonflow API 的写操作必须走 CLI 入口：

| 模块 | 入口函数 | 可用 op |
|------|----------|---------|
| 世界书 | `worldbook_op()` | `list`, `getWorld`, `save_create`, `save_update`, `import`, `export`, `delete` |
| 章节 | `chapters_op()` | `getChapter`, `save_create`, `save_update` |
| 客户端 | `client_op()` | `uploadImage` |

## 封面上传流程示例

```bash
# 1. 获取章节信息（走 chapters_op）
python -m src.cli toonflow chapters --story 谁让这个山大王修仙的 --op getChapter --entry-id 73

# 2. 上传图片（走 client_op）
python -m src.cli toonflow client --op uploadImage --entry /path/to/image.png --project-id 1

# 3. 保存章节更新（走 chapters_op）
python -m src.cli toonflow chapters --story 谁让这个山大王修仙的 --op save_update --entry-id 73 --entry '{json}'

# 组合使用（通过 workflow 函数）
python -m src.cli workflow chapter-background-img \
    --story 谁让这个山大王修仙的 \
    --chapter-id 73 \
    --cover images/ch1.png \
    --background images/ch1_bg.png
```

## 代码规范

```python
# ✅ 正确：通过 chapters_op 入口
from src.toonflow.chapters import chapters_op
chapter = chapters_op(story_name=story_name, op="getChapter", entry_id=chapter_id)
saved = chapters_op(story_name=story_name, op="save_update", entry_id=chapter_id, entry_json=json.dumps(data))

# ❌ 错误：直接调用内部函数
from src.toonflow.chapters import save_chapter_entry
saved = save_chapter_entry(client, story, entry)  # 违规！
```

## workflow 模块结构

```
src/toonflow/workflow/
├── README.md                    # 本文件
├── workflow_chapter_background_img.py  # 章节封面/背景图上传
└── ...
```
