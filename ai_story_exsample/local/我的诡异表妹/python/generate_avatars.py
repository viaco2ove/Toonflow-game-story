import urllib.request, json, os, subprocess, sys
from datetime import datetime

# 角色列表和提示词
characters = [
    {
        "name": "小七",
        "prompt": "一位黑色长发的少女，齐刘海，浅浅酒窝，嘴角带着温柔笑意，白色校服领口别着一枚黑色发卡，瞳孔隐约泛着竖瞳光泽，二次元动漫风格，半身像，柔和打光，细腻皮肤质感，略带神秘氛围",
    },
    {
        "name": "苏老师",
        "prompt": "一位容貌艳丽的年轻女性，黑色大波浪卷发，穿着得体的深色职业套装，嘴角挂着温柔迷人的微笑，眼神却深不见底，二次元动漫风格，半身像，精致妆容，优雅气质，美丽外表下暗藏危险气息",
    },
    {
        "name": "校长",
        "prompt": "一位五十多岁的儒雅男士，戴着金丝眼镜，一丝不苟的深色西装，温和而威严的微笑，眼神深邃如潭水，二次元动漫风格，半身像，成熟稳重气质，表面和蔼可亲却暗藏上位者威压",
    },
    {
        "name": "裂口女",
        "prompt": "一位身穿红色风衣的女性，长发遮住了大半张脸，只露出裂开到耳根的嘴角和无数尖牙，眼神空洞而疯狂，二次元恐怖动漫风格，半身像，暗红主色调，诡异而令人毛骨悚然的视觉冲击",
    },
    {
        "name": "无面人",
        "prompt": "一个穿着校服的少年，脸部是一片光滑无五官的皮肤，头顶裂开一张嘴，露出参差不齐的牙齿，坐姿僵硬，二次元恐怖动漫风格，半身像，灰白主色调，诡异而令人不安的怪异感",
    },
    {
        "name": "长发女",
        "prompt": "一位黑色超长头发的少女，头发遮住半张脸，只露出一只冰冷的眼睛，身穿白色睡衣，手中握着一把木梳，梳落的头发在地上微微蠕动，二次元恐怖动漫风格，半身像，暗色调，阴森而诡异的美感",
    },
    {
        "name": "李明",
        "prompt": "一位17岁少年，浓重的黑眼圈，略显脏乱的校服，眼神警惕地扫视四周，像一只受惊的麻雀，二次元动漫风格，半身像，疲惫而紧张的神情，瘦削的脸庞，凌乱的短发",
    },
    {
        "name": "王思远",
        "prompt": "一位17岁少年，戴着眼镜，校服整洁，手中拿着笔记本和笔，表情冷静若有所思，眼神中透着理性与分析的光芒，二次元动漫风格，半身像，学霸气质，干净利落的短发，斯文而沉稳",
    },
    {
        "name": "赵小胖",
        "prompt": "一位16岁微胖少年，圆脸，校服被撑得有点紧，脸上挂着憨厚的笑容，嘴角还沾着零食碎屑，二次元动漫风格，半身像，乐观开朗的神情，可爱的圆脸，眯起的眼睛，阳光而单纯",
    },
    {
        "name": "路人甲",
        "prompt": "一位面容普通的中年人，穿着学校工作人员的制服，表情平淡无奇，没有明显特征，二次元动漫风格，半身像，中性气质，模糊而不起眼的五官，随时可以融入任何场景",
    },
    {
        "name": "许飞",
        "prompt": "一位16岁少年，普通学生模样，穿着略显旧色的校服，表情困惑而警觉，眼神中带着误入异世界的不安，二次元动漫风格，半身像，平凡而真实的少年感，黑色短发，清秀但不出众的五官",
    },
]

# 路径配置
SKILL_DIR = "C:/Users/viaco/AppData/Local/Programs/WorkBuddy/resources/app.asar.unpacked/resources/builtin-skills/buddy-multimodal-generation"
SCRIPT_PATH = f"{SKILL_DIR}/scripts/buddy-cloud.py"
OUTPUT_DIR = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/我的诡异表妹/image"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 获取Token（通过环境变量传递）
token = os.environ.get("BUDDY_CLOUD_TOKEN", "")
if not token:
    print("错误: 未设置 BUDDY_CLOUD_TOKEN 环境变量")
    sys.exit(1)

print(f"输出目录: {OUTPUT_DIR}")
print(f"准备生成 {len(characters)} 个角色头像\n")

results = []

for idx, char in enumerate(characters):
    char_name = char["name"]
    char_prompt = char["prompt"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"avatar_{char_name}_{timestamp}.png"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    print(f"[{idx+1}/{len(characters)}] 正在生成: {char_name}")
    print(f"提示词长度: {len(char_prompt)} 字符")

    # 调用buddy-cloud.py生成图片
    cmd = [
        "python",
        SCRIPT_PATH,
        "image",
        char_prompt,
        "--resolution",
        "1024:1024",
        "--revise",
        "1",
    ]

    try:
        # 通过管道传递Token
        result = subprocess.run(
            cmd,
            input=token.encode("utf-8"),
            capture_output=True,
            text=False,
            timeout=600,
        )

        # 解析输出
        stdout_str = result.stdout.decode("utf-8", errors="replace")
        stderr_str = result.stderr.decode("utf-8", errors="replace")

        if stderr_str:
            print(f"日志: {stderr_str.strip()}")

        if result.returncode != 0:
            print(f"错误: 生成失败 (退出码 {result.returncode})")
            print(f"stdout: {stdout_str[:500]}")
            results.append({"name": char_name, "success": False, "error": "生成失败"})
            continue

        # 解析JSON输出
        try:
            output_json = json.loads(stdout_str)
            if output_json.get("status") != "DONE" or "result_url" not in output_json:
                print(f"错误: 无效的输出格式")
                print(f"输出: {stdout_str}")
                results.append({"name": char_name, "success": False, "error": "无效输出"})
                continue

            result_url = output_json["result_url"]
            if isinstance(result_url, list):
                result_url = result_url[0]

            print(f"成功! 图片URL: {result_url[:80]}...")

            # 下载图片
            print(f"正在下载到: {output_path}")
            download_cmd = ["curl", "-sS", "-L", "-o", output_path, result_url]
            download_result = subprocess.run(download_cmd, capture_output=True, timeout=60)

            if download_result.returncode != 0:
                print(f"警告: 下载失败 (退出码 {download_result.returncode})")
                results.append({"name": char_name, "success": False, "error": "下载失败"})
                continue

            results.append({"name": char_name, "success": True, "path": output_path, "url": result_url})
            print(f"保存成功: {output_path}\n")

        except json.JSONDecodeError:
            print(f"错误: 无法解析JSON输出")
            print(f"stdout: {stdout_str}")
            results.append({"name": char_name, "success": False, "error": "JSON解析失败"})

    except subprocess.TimeoutExpired:
        print(f"错误: 生成超时")
        results.append({"name": char_name, "success": False, "error": "超时"})
    except Exception as e:
        print(f"错误: {str(e)}")
        results.append({"name": char_name, "success": False, "error": str(e)})

# 汇总结果
print("\n" + "="*50)
print("生成汇总")
print("="*50)
success_count = sum(1 for r in results if r["success"])
print(f"成功: {success_count}/{len(results)}")

for r in results:
    if r["success"]:
        print(f"  ✓ {r['name']}: {os.path.basename(r['path'])}")
    else:
        print(f"  ✗ {r['name']}: {r['error']}")

# 保存结果到JSON
result_json_path = os.path.join(OUTPUT_DIR, "generation_results.json")
with open(result_json_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n结果已保存到: {result_json_path}")