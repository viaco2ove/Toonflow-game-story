"""
批量上传 通天传授-收徒系统(world_id=45) 的 14 个角色 webp 立绘到服务器
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.config import load_global_config
from src.toonflow.client import ToonflowClient
from src.toonflow.workflow.workflow_role_webp_avatar import upload_role_webp_avatar

cfg = load_global_config()
client = ToonflowClient(cfg)

STORY_NAME = "通天传授-收徒系统"
WORLD_ID = 45
CACHE_ROOT = ROOT / ".cache" / "character" / STORY_NAME

# 14 个角色：前端直接读 .cache，不需要区分生物/非生物
# 全部用 modnet webp 产物（小白/收徒系统之前也生成了）
ROLES = [
    "墨老", "小白", "收徒系统", "林惊鸿", "某女子", "某男子",
    "柳如烟", "玄尘长老", "玉玲珑", "苏沫", "萧肿", "陆川",
    "陈南璇", "黑袍使",
]

# 玩家角色（无 avatarVideoPath）
PLAYER_ROLES = {"陈南璇"}  # 如果陈南璇是玩家的话，先按NPC处理


def upload_one(role_name: str):
    webp_dir = CACHE_ROOT / role_name / "webp"
    if not webp_dir.exists():
        print(f"  ✗ {role_name}: 目录不存在 {webp_dir}")
        return False

    webp = webp_dir / "foreground.webp"
    bg = webp_dir / "background.png"
    first = webp_dir / "firstFrame.png"
    video = webp_dir / "video.mp4"

    # 读取时长
    duration_ms = None
    json_file = webp_dir / "webp.json"
    if json_file.exists():
        with open(json_file, encoding="utf-8") as f:
            info = json.load(f)
            duration_ms = info.get("duration_ms") or info.get("duration")

    missing = []
    if not webp.exists(): missing.append("foreground.webp")
    if not bg.exists(): missing.append("background.png")
    if not first.exists(): missing.append("firstFrame.png")
    if not video.exists(): missing.append("video.mp4")
    if missing:
        print(f"  △ {role_name}: 缺 {missing}")
        # 至少要有 webp 和 bg 才上传
        if not webp.exists() or not bg.exists():
            print(f"  ✗ {role_name}: 缺少核心文件，跳过")
            return False

    print(f"\n>>> 上传 {role_name}")
    try:
        result = upload_role_webp_avatar(
            story_name=STORY_NAME,
            role_name=role_name,
            webp_path=webp if webp.exists() else None,
            bg_path=bg if bg.exists() else None,
            first_frame_path=first if first.exists() else None,
            video_path=video if video.exists() else None,
            duration_ms=duration_ms,
            project_id=1,
            save=True,
            is_player=False,
        )
        print(f"  ✓ {role_name} 完成")
        return True
    except Exception as e:
        print(f"  ✗ {role_name} 失败: {e}")
        return False


if __name__ == "__main__":
    ok = fail = 0
    for role in ROLES:
        if upload_one(role):
            ok += 1
        else:
            fail += 1
    print(f"\n{'='*50}")
    print(f"完成: 成功 {ok}, 失败 {fail}")
