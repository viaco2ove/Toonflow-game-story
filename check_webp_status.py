"""诊断角色 webp 转换状态"""
import os, glob, sys

ROOT = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story"
CACHE = f"{ROOT}/.cache/character/黑塔：从超忆症开始成神"
SKILL = f"{ROOT}/.workbuddy/skills/convert-avatar-video-to-webp/convert.py"

ROLES = ["陈曦", "张晚意", "林凡", "老周", "苏晓", "魏叔", "陈母", "百晓生", "白子轩", "小满", "某女子", "某男子"]

for role in ROLES:
    role_dir = f"{CACHE}/{role}"
    webp_dir = f"{role_dir}/webp"
    mp4s = glob.glob(f"{role_dir}/*.mp4")
    webp_ok = os.path.isfile(f"{webp_dir}/foreground.webp") if os.path.isdir(webp_dir) else False
    bg_ok = os.path.isfile(f"{webp_dir}/background.png") if os.path.isdir(webp_dir) else False
    mp4_info = mp4s[0] if mp4s else "❌ 无 mp4"
    status = "✅" if webp_ok and bg_ok else "❌ 缺失"
    print(f"{status} {role}: mp4={mp4_info.split('/')[-1] if mp4_info else '无'}")
