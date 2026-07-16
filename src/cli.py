#!/usr/bin/env python3
"""
Toonflow Game Story - 统一命令行工具

用法:
    # Toonflow 故事更新
    python -m src.cli toonflow update --story 破局-从冷落走到瞩目
    python -m src.cli toonflow update --story 我的诡异表妹

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
    if g.ai_story_local_dir.exists():
        stories = [d.name for d in g.ai_story_local_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        print(f"可用故事 ({g.ai_story_local_dir}):")
        for s in sorted(stories):
            # 检查是否有 .env 或 story.json
            env_file = g.ai_story_local_dir / s / ".env"
            json_file = g.ai_story_local_dir / s / "story.json"
            marker = ""
            if json_file.exists():
                marker = " [story.json]"
            elif env_file.exists():
                marker = " [.env]"
            print(f"  - {s}{marker}")
    else:
        print(f"故事目录不存在: {g.ai_story_local_dir}")


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

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()