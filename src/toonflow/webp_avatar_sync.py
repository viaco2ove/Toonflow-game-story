"""
webp_avatar_sync.py - 把本地生成的角色视频头像(.mp4)上传到 Toonflow 服务器，
转成 webp 动画头像 + png 背景，并可写回世界角色数据。

流程:
  1. 读 mp4 -> base64 -> data:video/mp4;base64,...
  2. POST /game/convertAvatarVideoToGif  提交转换任务 (返回 taskId)
  3. 轮询 POST /game/convertAvatarVideoToGif/status  直到 status=success
  4. (可选) 把 foregroundFilePath(webp)/backgroundFilePath(png)/videoPath 写回角色

用法:
  python -m src.cli webp-sync --mp4 path/to/role.mp4
  python -m src.cli webp-sync --mp4 role.mp4 --world-id 44 --role-name 先生
"""
import sys
import os
import argparse
import base64
import time
import json
from pathlib import Path

# 允许从项目根目录直接运行
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.config import load_global_config
from src.toonflow.client import ToonflowClient


def convert_video_to_webp(client: ToonflowClient, mp4_path: str,
                           project_id: int = 1,
                           poll_interval: int = 3,
                           max_wait: int = 360) -> dict:
    """上传 mp4，转换为 webp 动画头像，返回最终 status data"""
    mp4_path = Path(mp4_path)
    if not mp4_path.exists():
        raise FileNotFoundError(f"找不到 mp4: {mp4_path}")

    file_size = mp4_path.stat().st_size
    print(f"  -> 读取 mp4: {mp4_path.name} ({file_size / 1024:.1f} KB)")
    with open(mp4_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    base64_data = f"data:video/mp4;base64,{b64}"
    print(f"  -> base64 编码完成 ({len(b64) / 1024:.1f} KB)，提交转换任务...")

    payload = {
        "projectId": project_id,
        "fileName": mp4_path.name,
        "base64Data": base64_data,
    }
    result = client.api_call("/game/convertAvatarVideoToGif", payload, timeout=120)
    if result.get("code") != 200:
        raise Exception(f"提交转换任务失败: {result}")
    task_id = result["data"]["taskId"]
    print(f"  ✓ 任务已提交 taskId={task_id}")

    waited = 0
    last_progress = -1
    while waited < max_wait:
        st = client.api_call("/game/convertAvatarVideoToGif/status",
                             {"taskId": task_id}, timeout=30)
        data = st.get("data", {})
        status = data.get("status")
        progress = data.get("progress")
        if progress != last_progress:
            print(f"  ... status={status} progress={progress} msg={data.get('message', '')}")
            last_progress = progress
        if status == "success":
            return data
        if status == "failed":
            raise Exception(f"转换失败: {data.get('errorMessage')}")
        time.sleep(poll_interval)
        waited += poll_interval

    raise TimeoutError(f"转换超时（已等待 {max_wait}s）")


def sync_to_role(client: ToonflowClient, world_id: int,
                 role_name: str, conv_data: dict) -> dict:
    """把转换结果写回世界中的指定角色"""
    world = client.get_world(world_id)
    settings = world.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)

    roles = settings.get("roles", [])
    target = None
    for r in roles:
        if r.get("name") == role_name:
            target = r
            break
    if not target and world.get("playerRole", {}).get("name") == role_name:
        target = world["playerRole"]

    if not target:
        raise Exception(f"世界 {world_id} 中未找到角色「{role_name}」")

    target["avatarPath"] = conv_data.get("foregroundFilePath")      # webp 动画
    target["avatarBgPath"] = conv_data.get("backgroundFilePath")    # png 背景
    target["avatarVideoPath"] = conv_data.get("videoPath")          # 原 mp4
    target["avatarFirstFramePath"] = conv_data.get("firstFramePath")
    target["avatarDurationMs"] = conv_data.get("durationMs")

    # ⚠️ 关键：必须补 worldId，否则 saveWorld 会当成 worldId=0 新建一个世界（重复故事）
    #    get_world 返回的字段只有 id 没有 worldId，full_update.py 也是显式补 worldId 后才 save_world
    world["id"] = world_id
    world["worldId"] = world_id
    client.save_world(world)
    print(f"  ✓ 已写回角色「{role_name}」(world {world_id})")
    return target


def main():
    parser = argparse.ArgumentParser(description="mp4 视频头像转 webp 并同步到角色")
    parser.add_argument("--mp4", required=True, help="本地 mp4 视频头像路径")
    parser.add_argument("--project-id", type=int, default=1)
    parser.add_argument("--world-id", type=int, default=None,
                        help="写回目标世界 ID（需配合 --role-name）")
    parser.add_argument("--role-name", default=None,
                        help="写回目标角色名（需配合 --world-id）")
    parser.add_argument("--no-poll-limit", type=int, default=360,
                        help="最大轮询等待秒数")
    args = parser.parse_args()

    cfg = load_global_config()
    client = ToonflowClient(cfg)

    data = convert_video_to_webp(client, args.mp4, args.project_id,
                                 max_wait=args.no_poll_limit)

    print("\n=== 转换结果 ===")
    print(f"  webp (foreground): {data.get('foregroundFilePath')}")
    print(f"  bg  (background):  {data.get('backgroundFilePath')}")
    print(f"  video:            {data.get('videoPath')}")
    print(f"  firstFrame:       {data.get('firstFramePath')}")
    print(f"  durationMs:       {data.get('durationMs')}")

    if args.world_id and args.role_name:
        sync_to_role(client, args.world_id, args.role_name, data)
    elif args.world_id or args.role_name:
        print("  ⚠ 写回需要同时提供 --world-id 和 --role-name，已跳过")


if __name__ == "__main__":
    main()
