"""全量批量：13 个角色转换 + 写回 world 44
先生和陈曦先跳过转换，先生已有 webp，陈曦用旧版 mp4 先写回静态 avatar。
"""
import sys, os, time, json
sys.path.insert(0, ".")
from src.config import load_global_config
from src.toonflow.client import ToonflowClient
from src.toonflow.webp_avatar_sync import convert_video_to_webp, sync_to_role

cfg = load_global_config()
cli = ToonflowClient(cfg)

WORLD_ID = 44
STORY = "黑塔：从超忆症开始成神"
CACHE_BASE = f".cache/character/{STORY}"

ROLES = [
    "先生",      # 已有 webp，跳过转换
    "陈曦",      # 有旧版 mp4，先用静态 avatar 写回
    "张晚意", "林凡", "老周", "苏晓", "魏叔", "陈母",
    "百晓生", "白子轩", "小满", "某女子", "某男子",
]
# 百晓生已单独成功，追加结果
DONE = {"百晓生": {"foregroundFilePath": "/1/game/role/051a0cc6-e426-4b1c-963a-4cf74358bad0.webp",
                   "backgroundFilePath": "/1/game/role/5d789c8d-9f74-486a-82b2-cdd29065bdff.png",
                   "videoPath": "http://127.0.0.1:60002/1/game/role/72ba1086-1888-4d30-81b9-4a0d35c20ea6.mp4"}}

def get_mp4(role):
    cache_dir = os.path.join(CACHE_BASE, role)
    if not os.path.isdir(cache_dir):
        return None
    mp4s = sorted([f for f in os.listdir(cache_dir) if f.endswith(".mp4")], reverse=True)
    return os.path.join(cache_dir, mp4s[0]) if mp4s else None

def sync_role(role, conv_data):
    """写回 world"""
    try:
        sync_to_role(cli, WORLD_ID, role, conv_data)
        print(f"[{role}] ✅ 写回成功")
    except Exception as e:
        print(f"[{role}] ❌ 写回失败: {e}")

# ---- 1. 先生 直接写回（已有 webp，world 里先生字段应该完整了，跳过） ----
print("=== 先生：检查 world 中状态 ===")
w = cli.get_world(WORLD_ID)
settings = w.get("settings", {})
if isinstance(settings, str):
    settings = json.loads(settings)
for r in settings.get("roles", []):
    if r.get("name") == "先生":
        print(f"  先生 avatarPath={r.get('avatarPath')} bg={r.get('avatarBgPath')}")
        break
for r in ([w.get("playerRole")] if w.get("playerRole") else []):
    if r and r.get("name") == "先生":
        print(f"  (player) 先生 avatarPath={r.get('avatarPath')}")

# ---- 2. 陈曦：先拿世界数据看现有状态 ----
print("=== 陈曦：检查状态 ===")
player = w.get("playerRole", {})
if player.get("name") == "陈曦":
    print(f"  陈曦(player) 当前 avatarPath={player.get('avatarPath')}")
    # 陈曦没有 webp，用静态图先写回，等后续有 webp 再更新
    # 但先不动player，避免覆盖已有数据

# ---- 3. 其余角色并行转换（先生跳过，陈曦暂时跳过）----
NEED_CONVERT = ["张晚意", "林凡", "老周", "苏晓", "魏叔", "陈母", "白子轩", "小满", "某女子", "某男子"]

print(f"\n=== 开始转换 {len(NEED_CONVERT)} 个角色 ===")
conv_results = {}

for role in NEED_CONVERT:
    mp4 = get_mp4(role)
    if not mp4:
        print(f"[{role}] ❌ 无 mp4")
        continue
    print(f"[{role}] -> {os.path.basename(mp4)}")
    try:
        result = convert_video_to_webp(cli, mp4, project_id=1, max_wait=600)
        conv_results[role] = result
        print(f"[{role}] ✅ 转换成功")
    except Exception as e:
        print(f"[{role}] ❌ 转换失败: {e}")

# ---- 4. 合并所有结果 ----
all_results = {}
all_results.update(DONE)
all_results.update(conv_results)

# ---- 5. 批量写回 world（一次 fetch + 多次修改 + 一次 save）----
print("\n=== 写回 world 44 ===")
w2 = cli.get_world(WORLD_ID)
settings2 = w2.get("settings", {})
if isinstance(settings2, str):
    settings2 = json.loads(settings2)
roles2 = settings2.get("roles", [])
player2 = w2.get("playerRole", {})

for role_name, conv in all_results.items():
    fg = conv.get("foregroundFilePath", "")
    bg = conv.get("backgroundFilePath", "")
    vid = conv.get("videoPath", "")
    matched = False
    for r in roles2:
        if r.get("name") == role_name:
            r["avatarPath"] = fg
            r["avatarBgPath"] = bg
            r["videoPath"] = vid
            print(f"  [{role_name}] NPC -> fg={fg[:50]}...")
            matched = True
            break
    if not matched and player2.get("name") == role_name:
        player2["avatarPath"] = fg
        player2["avatarBgPath"] = bg
        player2["videoPath"] = vid
        print(f"  [{role_name}] player -> fg={fg[:50]}...")

# playerRole 可能单独存在
if "陈曦" not in all_results and player2.get("name") == "陈曦":
    # 用静态图（不变），等 webp 转换
    pass

settings2["roles"] = roles2
w2["settings"] = json.dumps(settings2)
w2["worldId"] = WORLD_ID
w2["id"] = WORLD_ID

cli.save_world(w2)
print("\n=== 完成 ===")