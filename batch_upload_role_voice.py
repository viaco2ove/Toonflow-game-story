"""
批量上传角色音色文件并绑定到故事

用法:
    python batch_upload_role_voice.py <story_name>

约定:
    - .cache/character/<story_name>/<role_name>/<role_name>_voice.wav
    - 玩家角色映射: 缓存"陆川" → 服务器"用户"（is_player=True）
    - 已绑定的角色会跳过（避免重复上传）
    - 失败的角色会记录到 _batch_log.txt
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.toonflow.client import world_op
from src.toonflow.workflow.workflow_voice_file_up_save import upload_role_voice_and_save


# 缓存目录名 → 服务器角色配置
# 陆川（缓存） → 用户（服务器玩家）
PLAYER_MAPPING = {
    "陆川": "用户",
}


def batch_upload_all_voices(story_name: str, skip_bound: bool = True):
    """
    批量上传所有角色的音色

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
    bound_names = {r.get("name") for r in roles if r.get("voiceReferenceAudioPath")}

    pr = world.get("playerRole")
    import json
    if isinstance(pr, str):
        pr = json.loads(pr)
    player_name = pr.get("name") if pr else None
    player_bound = bool(pr.get("voiceReferenceAudioPath")) if pr else False

    # 2. 遍历 .cache 下的角色目录
    role_dirs = sorted([d for d in cache_root.iterdir() if d.is_dir()])

    log_lines = []
    success_count = 0
    skip_count = 0
    fail_count = 0

    print("=" * 60)
    print(f"批量上传音色: {story_name}")
    print(f"  已绑定 NPC: {len([n for n in bound_names])} 个")
    print(f"  玩家已绑: {'是' if player_bound else '否'}")
    print("=" * 60)

    for role_dir in role_dirs:
        cache_name = role_dir.name  # 缓存目录名

        # 找 wav 文件
        wav_files = list(role_dir.glob("*_voice.wav"))
        if not wav_files:
            continue
        wav_path = wav_files[0]

        # 决定服务器角色名和路径
        if cache_name in PLAYER_MAPPING:
            server_name = PLAYER_MAPPING[cache_name]
            is_player = True
            if skip_bound and player_bound:
                print(f"\n⏭  跳过 玩家({server_name})（已绑定）")
                skip_count += 1
                continue
        else:
            server_name = cache_name
            is_player = False
            if server_name not in {r.get("name") for r in roles}:
                print(f"\n⏭  跳过 {cache_name}（服务器无此角色）")
                skip_count += 1
                continue
            if skip_bound and server_name in bound_names:
                print(f"\n⏭  跳过 {server_name}（已绑定）")
                skip_count += 1
                continue

        # 执行上传
        target_label = "玩家" if is_player else "NPC"
        print(f"\n{'='*60}")
        print(f"处理 {target_label}: {cache_name} → {server_name}")
        print(f"  音色文件: {wav_path.name}")
        print(f"{'='*60}")
        try:
            upload_role_voice_and_save(
                story_name=story_name,
                role_name=server_name,
                audio_path=wav_path,
                voice_mode="clone",
                reference_text="",
                project_id=1,
                save=True,
                is_player=is_player,
            )
            success_count += 1
            log_lines.append(f"✓ {cache_name} → {server_name}")
        except Exception as e:
            fail_count += 1
            err_msg = f"✗ {cache_name} → {server_name}: {e}"
            print(f"\n{err_msg}")
            log_lines.append(err_msg)

    # 3. 汇总
    print("\n" + "=" * 60)
    print(f"批量上传音色完成: 成功 {success_count} / 跳过 {skip_count} / 失败 {fail_count}")
    print("=" * 60)

    log_path = cache_root / "_batch_voice_upload_log.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"故事: {story_name}\n\n")
        f.write("\n".join(log_lines))
        f.write(f"\n\n汇总: 成功 {success_count} / 跳过 {skip_count} / 失败 {fail_count}\n")
    print(f"日志已写入: {log_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python batch_upload_role_voice.py <story_name>")
        print("示例: python batch_upload_role_voice.py 通天传授-收徒系统")
        sys.exit(1)
    batch_upload_all_voices(sys.argv[1], skip_bound=True)