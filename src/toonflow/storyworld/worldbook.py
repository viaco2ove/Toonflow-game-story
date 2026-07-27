"""
世界书维护：对故事世界书的 增删改查 + 导入导出

本地数据源: {story_dir}/worldbook/worldbook.json
服务端: 通过 ToonflowClient 调 game-app 的 4 个世界书 API

用法:
    from src.toonflow.storyworld.worldbook import (
        list_worldbook, import_worldbook, export_worldbook,
        save_worldbook_entry, delete_worldbook_entry,
    )

    或命令行:
    python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op list
    python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op import
    python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op export
"""
import json
from pathlib import Path

from src.config import GlobalConfig, StoryConfig, load_config
from src.toonflow.client import ToonflowClient


def _worldbook_path(story: StoryConfig) -> Path:
    """本地 worldbook.json 路径"""
    return story.story_dir / "worldbook" / "worldbook.json"


def _load_local_worldbook(story: StoryConfig) -> list:
    """读取本地 worldbook.json，返回 entries 列表（兼容 {entries:[...]} 顶层结构）"""
    path = _worldbook_path(story)
    if not path.exists():
        raise FileNotFoundError(f"本地世界书不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return data["entries"]
    return []


def _save_local_worldbook(story: StoryConfig, entries: list, meta: dict = None):
    """把条目列表写回本地 worldbook.json（带元信息壳）"""
    path = _worldbook_path(story)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": story.story_name,
        "version": "1.0.0",
        "totalEntries": len(entries),
        **(meta or {}),
        "entries": entries,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def _strip_entry_for_export(entry: dict) -> dict:
    """导出时去掉服务端字段（id/worldId/createTime/updateTime），保留逻辑字段"""
    return {
        k: v for k, v in entry.items()
        if k not in ("id", "worldId", "createTime", "updateTime")
    }


def list_worldbook(client: ToonflowClient, story: StoryConfig, verbose: bool = True) -> list:
    """列出服务端该世界的全部世界书条目"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    entries = client.list_world_book(story.world_id)
    if verbose:
        print(f"  ✓ 服务端世界书条目: {len(entries)} 条 (world_id={story.world_id})")
        for i, e in enumerate(entries, 1):
            tag = "[常驻]" if e.get("constant") else ""
            keys = "、".join(e.get("keys", [])[:3])
            print(f"    {i:>3}. {tag}{e.get('title', '(无标题)')} [{e.get('category', '?')}] {keys}")
    return entries


def import_worldbook(client: ToonflowClient, story: StoryConfig, mode: str = "replace") -> dict:
    """把本地 worldbook.json 导入服务端。mode: replace(覆盖) / merge(追加)"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    entries = _load_local_worldbook(story)
    print(f"  -> 本地 worldbook.json: {len(entries)} 条，导入模式={mode}")
    if not entries:
        print("  ⚠ 本地无条目可导入")
        return {"imported": 0, "deleted": 0, "mode": mode}
    result = client.import_world_book(story.world_id, entries, mode)
    imported = result.get("imported", 0)
    deleted = result.get("deleted", 0)
    suffix = f"，替换旧 {deleted} 条" if deleted else ""
    print(f"  ✓ 导入完成: 新增 {imported} 条{suffix}")
    return result


def export_worldbook(client: ToonflowClient, story: StoryConfig) -> Path:
    """从服务端拉取全部条目，写回本地 worldbook.json"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    entries = client.list_world_book(story.world_id)
    cleaned = [_strip_entry_for_export(e) for e in entries]
    path = _save_local_worldbook(story, cleaned)
    print(f"  ✓ 导出 {len(cleaned)} 条到本地: {path}")
    return path


def save_worldbook_entry(client: ToonflowClient, story: StoryConfig, entry: dict) -> dict:
    """新建或更新单条世界书条目（entry.id 有值则更新，无值则新建）"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    saved = client.save_world_book_entry(story.world_id, entry)
    action = "更新" if entry.get("id") else "新建"
    print(f"  ✓ {action}条目: {saved.get('title', '')} (id={saved.get('id')})")
    return saved


def delete_worldbook_entry(client: ToonflowClient, story: StoryConfig, entry_id: int) -> bool:
    """删除单条世界书条目"""
    if not story.world_id:
        raise ValueError("story.world_id 为空，请先创建/绑定世界")
    client.delete_world_book_entry(entry_id)
    print(f"  ✓ 删除条目 id={entry_id}")
    return True


def worldbook_op(story_name: str = None, op: str = "list", mode: str = "replace",
                 entry_json: str = None, entry_id: int = None):
    """
    世界书操作入口（供 cli 调用）

    op:
      list    - 列出服务端条目
      import  - 本地 json 导入服务端（mode 控制覆盖/追加）
      export  - 服务端条目导出到本地 json
      save    - 新建/更新单条（--entry 传 JSON 字符串）
      delete  - 删除单条（--entry-id 传 id）
    """
    global_cfg, story = load_config(story_name)
    if not story:
        raise ValueError("未指定故事名，且 .env 中无 CURRENT_STORY")

    print("=" * 60)
    print(f"世界书维护: {story.story_name}")
    print(f"环境: {global_cfg.base_url} | World ID: {story.world_id}")
    print(f"操作: {op}")
    print("=" * 60)

    client = ToonflowClient(global_cfg)

    if op == "list":
        list_worldbook(client, story)
    elif op == "import":
        import_worldbook(client, story, mode=mode)
    elif op == "export":
        export_worldbook(client, story)
    elif op == "save":
        if not entry_json:
            raise ValueError("save 操作需要 --entry 传 JSON 字符串")
        entry = json.loads(entry_json)
        save_worldbook_entry(client, story, entry)
    elif op == "delete":
        if not entry_id:
            raise ValueError("delete 操作需要 --entry-id 传条目 id")
        delete_worldbook_entry(client, story, entry_id)
    else:
        raise ValueError(f"未知操作: {op}（支持: list/import/export/save/delete）")
