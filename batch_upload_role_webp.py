"""
批量上传故事角色立绘一角三图

用法:
    python batch_upload_role_webp.py <story_name>

约定:
    - .cache/character/<story_name>/<role_name>/webp/
        - foreground.webp  → avatarPath
        - background.png   → avatarBgPath
        - firstFrame.png   → avatarFirstFramePath
        - video.mp4        → avatarVideoPath（仅 NPC）
        - webp.json        → 含 durationMs / ok 字段
    - 玩家角色（playerRole）没有本地缓存，跳过
    - 已绑定的角色会跳过（避免重复上传）
    - 失败的角色会记录到 _batch_log.txt
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.toonflow.client import world_op
from src.toonflow.workflow.workflow_role_webp_avatar import upload_role_webp_avatar


def _load_webp_meta(role_dir: Path) -> dict:
    """从 webp.json 读 durationMs 等元数据"""
    meta_path = role_dir / "webp.json"
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def batch_upload_all_roles(story_name: str, skip_bound: bool = True):
    """
    批量上传所有角色的立绘

    Args:
        story_name: 故事名
        skip_bound: 是否跳过已绑定的角色（默认 True）
    """
    cache_root = ROOT / ".cache" / "character" / story_name
    if not cache_root.exists():
        raise FileNotFoundError(f"角色缓存目录不存在: {cache_root}")

    # 1. 拉世界数据，区分已绑定 / 未绑定
    world = world_op(story_name=story_name, op="get")
    if not world:
        raise Exception("无法获取世界数据")

    settings = world.get("settings")
    if isinstance(settings, str):
        settings = json.loads(settings)
    roles = (settings or {}).get("roles", [])

    # 已绑定角色名集合
    bound_names = {r.get("name") for r in roles if r.get("avatarPath")}

    # 玩家角色（单独处理，暂跳过）
    pr = world.get("playerRole")
    if isinstance(pr, str):
        pr = json.loads(pr)
    player_name = pr.get("name") if pr else None

    # 2. 遍历 .cache 下的角色目录
    role_dirs = sorted([d for d in cache_root.iterdir() if d.is_dir() and (d / "webp").exists()])

    log_lines = []
    success_count = 0
    skip_count = 0
    fail_count = 0

    print("=" * 60)
    print(f"批量上传: {story_name}")
    print(f"  玩家角色: {player_name} (跳过，无本地缓存)")
    print(f"  待处理 NPC: {len(role_dirs)}")
    print("=" * 60)

    for role_dir in role_dirs:
        role_name = role_dir.name

        # 跳过已绑定
        if skip_bound and role_name in bound_names:
            print(f"\n⏭  跳过 {role_name}（已绑定）")
            skip_count += 1
            continue

        # 校验文件
        webp_dir = role_dir / "webp"
        fg = webp_dir / "foreground.webp"
        bg = webp_dir / "background.png"
        ff = webp_dir / "firstFrame.png"
        vid = webp_dir / "video.mp4"
        meta = _load_webp_meta(role_dir)
        duration = meta.get("durationMs")

        if not fg.exists():
            print(f"\n⏭  跳过 {role_name}（缺 foreground.webp）")
            skip_count += 1
            continue

        # 执行上传
        print(f"\n{'='*60}")
        print(f"处理: {role_name}")
        print(f"{'='*60}")
        try:
            upload_role_webp_avatar(
                story_name=story_name,
                role_name=role_name,
                webp_path=fg if fg.exists() else None,
                bg_path=bg if bg.exists() else None,
                first_frame_path=ff if ff.exists() else None,
                video_path=vid if vid.exists() else None,
                duration_ms=duration,
                project_id=1,
                save=True,
                is_player=False,
            )
            success_count += 1
            log_lines.append(f"✓ {role_name}")
        except Exception as e:
            fail_count += 1
            err_msg = f"✗ {role_name}: {e}"
            print(f"\n{err_msg}")
            log_lines.append(err_msg)

    # 3. 汇总
    print("\n" + "=" * 60)
    print(f"批量上传完成: 成功 {success_count} / 跳过 {skip_count} / 失败 {fail_count}")
    print("=" * 60)

    log_path = cache_root / "_batch_upload_log.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"故事: {story_name}\n")
        f.write(f"玩家角色: {player_name} (跳过)\n\n")
        f.write("\n".join(log_lines))
        f.write(f"\n\n汇总: 成功 {success_count} / 跳过 {skip_count} / 失败 {fail_count}\n")
    print(f"日志已写入: {log_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python batch_upload_role_webp.py <story_name>")
        print("示例: python batch_upload_role_webp.py 通天传授-收徒系统")
        sys.exit(1)
    batch_upload_all_roles(sys.argv[1], skip_bound=True)