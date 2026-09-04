#!/usr/bin/env python3
"""
Toonflow Game Story - 统一命令行工具

用法:
    # Toonflow 故事更新
    python -m src.cli toonflow update --story 破局-从冷落走到瞩目
    python -m src.cli toonflow update --story 我的诡异表妹

    # 世界书维护
    python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op list
    python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op import
    python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op import --mode merge
    python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op export

    # 角色卡构建
    python -m src.cli cards build --story 破局-从冷落走到瞩目
    python -m src.cli cards build --story 我的诡异表妹 --output chub_ai

    # 上传到 chub.ai
    python -m src.cli cards chub --story 破局-从冷落走到瞩目
    python -m src.cli cards chub --story 我的诡异表妹 --name 顾子航
    python -m src.cli cards chub --story 我的诡异表妹 --avatar-only

    # 上传到 cards.sillytavern.one
    python -m src.cli cards sillytavern --story 破局-从冷落走到瞩目
    python -m src.cli cards sillytavern --story 破局-从冷落走到瞩目 --name 顾子航

    # 列出所有故事
    python -m src.cli list-stories
"""
import argparse
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_global_config


def cmd_toonflow_update(args):
    """Toonflow 故事完整更新"""
    from src.toonflow.full_update import full_update
    full_update(args.story)


def cmd_toonflow_worldbook(args):
    """世界书维护：list/import/export/save/delete"""
    from src.toonflow.storyworld.worldbook import worldbook_op
    worldbook_op(
        story_name=args.story,
        op=args.op,
        mode=args.mode,
        entry_json=args.entry,
        entry_id=int(args.entry_id) if args.entry_id else None,
    )


def cmd_worldbook_build(args):
    """构建世界书：MD → worldbook.json"""
    from src.toonflow.storyworld.worldbook_builder import build_and_save
    from src.config import load_config
    if args.story:
        global_cfg, story = load_config(args.story)
    else:
        global_cfg, story = load_config()
    if not story:
        raise ValueError("未指定故事名，且 .env 中无 CURRENT_STORY")
    build_and_save(str(story.story_dir))


def cmd_cards_build(args):
    """构建角色卡"""
    from src.cards.builder import build_all_cards
    build_all_cards(args.story, output_subdir=args.output)


def cmd_cards_chub(args):
    """上传到 chub.ai"""
    from src.cards.chub_ai import upload_to_chub
    names = [args.name] if args.name else None
    upload_to_chub(args.story, card_names=names, avatar_only=args.avatar_only)


def cmd_cards_sillytavern(args):
    """上传到 cards.sillytavern.one"""
    from src.cards.sillytavern import upload_to_cards
    names = [args.name] if args.name else None
    upload_to_cards(args.story, card_names=names, relogin=args.relogin)


def cmd_list_stories(args):
    """列出所有可用故事"""
    g = load_global_config()
    seen = set()
    for story_root in g.ai_story_dirs:
        if not story_root.exists():
            continue
        stories = [d for d in story_root.iterdir() if d.is_dir() and not d.name.startswith(".") and d.name not in seen]
        if not stories:
            continue
        print(f"故事目录: {story_root}")
        for s in sorted(stories, key=lambda x: x.name):
            seen.add(s.name)
            env_file = s / ".env"
            json_file = s / "story.json"
            marker = ""
            if json_file.exists():
                marker = " [story.json]"
            elif env_file.exists():
                marker = " [.env]"
            print(f"  - {s.name}{marker}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Toonflow Game Story - 统一工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # toonflow update
    p_tf = subparsers.add_parser("toonflow", help="Toonflow 故事更新")
    p_tf_sub = p_tf.add_subparsers(dest="action")
    p_update = p_tf_sub.add_parser("update", help="完整更新（世界+角色+章节+封面）")
    p_update.add_argument("--story", "-s", required=True, help="故事名")
    p_update.set_defaults(func=cmd_toonflow_update)

    # toonflow worldbook：世界书维护
    p_wb = p_tf_sub.add_parser("worldbook", help="世界书维护（list/import/export/save/delete）")
    p_wb.add_argument("--story", "-s", required=True, help="故事名")
    p_wb.add_argument("--op", default="list",
                      choices=["list", "import", "export", "save", "delete"],
                      help="操作: list(列出服务端) / import(本地导入服务端) / export(服务端导出本地) / save(新建更新单条) / delete(删除单条)")
    p_wb.add_argument("--mode", default="replace", choices=["replace", "merge"],
                      help="import 时的模式: replace(覆盖) / merge(追加)，默认 replace")
    p_wb.add_argument("--entry", default=None, help="save 操作时传入的条目 JSON 字符串")
    p_wb.add_argument("--entry-id", default=None, help="delete 操作时的条目 id")
    p_wb.set_defaults(func=cmd_toonflow_worldbook)

    # toonflow worldbook-build：MD → worldbook.json
    p_wbb = p_tf_sub.add_parser("worldbook-build", help="构建世界书 MD → worldbook.json")
    p_wbb.add_argument("--story", "-s", default=None, help="故事名（不指定则用 CURRENT_STORY）")
    p_wbb.set_defaults(func=cmd_worldbook_build)

    # cards
    p_cards = subparsers.add_parser("cards", help="角色卡构建和上传")
    p_cards_sub = p_cards.add_subparsers(dest="action")

    p_build = p_cards_sub.add_parser("build", help="构建角色卡")
    p_build.add_argument("--story", "-s", required=True, help="故事名")
    p_build.add_argument("--output", "-o", default=None, help="输出子目录（如 chub_ai）")
    p_build.set_defaults(func=cmd_cards_build)

    p_chub = p_cards_sub.add_parser("chub", help="上传到 chub.ai")
    p_chub.add_argument("--story", "-s", required=True, help="故事名")
    p_chub.add_argument("--name", "-n", default=None, help="指定角色名（不指定则全部）")
    p_chub.add_argument("--avatar-only", action="store_true", help="只上传头像")
    p_chub.set_defaults(func=cmd_cards_chub)

    p_st = p_cards_sub.add_parser("sillytavern", help="上传到 cards.sillytavern.one")
    p_st.add_argument("--story", "-s", required=True, help="故事名")
    p_st.add_argument("--name", "-n", default=None, help="指定角色名")
    p_st.add_argument("--relogin", action="store_true", help="强制重新登录")
    p_st.set_defaults(func=cmd_cards_sillytavern)

    # list-stories
    p_list = subparsers.add_parser("list-stories", help="列出所有可用故事")
    p_list.set_defaults(func=cmd_list_stories)

    # agme_cache pull
    p_agme = subparsers.add_parser("agme_cache", help="从服务端拉取数据到 toonflow_agme_cache 目录")
    p_agme.add_argument("--story", "-s", default=None, help="故事名（不指定则用 CURRENT_STORY）")
    p_agme.add_argument("--world-id", default=None, help="world ID（不指定则从 story.json 读取）")
    p_agme.add_argument("--project-id", default=None, help="project ID，默认 1")
    p_agme.set_defaults(func=lambda a: __import__("src.toonflow.agme_cache", fromlist=["cmd_agme_cache_pull"]).cmd_agme_cache_pull(a))

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()