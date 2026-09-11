# 特别注意
只运行调用 --op 里的函数，不允许直接调用save_chapter_entry 等内部函数 这种违规操作。

## 封面上传流程
```
"""
【api_help/image_api/封面上传.md】
python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op getWorld {worldId}
python -m src.cli toonflow chapters --story 谁让这个山大王修仙的 --op getChapter {chapter_id}
python -m src.cli toonflow client --op uploadImage --entry /path/to/image.png
python -m src.cli toonflow chapters --story 谁让这个山大王修仙的 --op save_update xxx
python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op save_update xxx
"""
```
