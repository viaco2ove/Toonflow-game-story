#!/usr/bin/env python3
"""
Toonflow 角色 → SillyTavern V2 角色卡转换器

功能：
  1. 读取 Toonflow 角色 MD 文件
  2. 解析参数卡 JSON + 文本设定
  3. 转换为 SillyTavern V2 角色卡格式 (chara_card_v2)
  4. 将 JSON 以 base64 编码嵌入头像 PNG 的 tEXt chunk (keyword=chara)
  5. 同时输出独立 JSON 版本
  6. 输出到 characters_repo/破局-从冷落走到瞩目/

用法:
  python build_cards.py
"""

import json
import re
import os
import base64
import struct
import zlib
from pathlib import Path
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from dotenv import load_dotenv

# ============ 配置加载 ============
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ENV_FILE = PROJECT_DIR / ".env"
load_dotenv(ENV_FILE)

# ============ 路径配置（从环境变量读取）============
def get_path(key, fallback):
    """读取环境变量路径，支持绝对路径或相对路径（相对于 PROJECT_DIR）"""
    val = os.getenv(key, fallback)
    p = Path(val)
    if p.is_absolute():
        return p
    return PROJECT_DIR / p

CURRENT_STORY = os.getenv("CURRENT_STORY", "破局-从冷落走到瞩目")
AI_STORY_LOCAL_DIR = get_path("AI_STORY_LOCAL_DIR", "ai_story/local")
AVATARS_SUBDIR = os.getenv("AVATARS_SUBDIR", "bak1")

STORY_DIR = AI_STORY_LOCAL_DIR / CURRENT_STORY
ROLES_DIR = STORY_DIR / "roles"
AVATARS_DIR = STORY_DIR / "avatars" / AVATARS_SUBDIR
OUTPUT_DIR = SCRIPT_DIR / CURRENT_STORY

# ============ 全局背景（场景设定）============
SCENARIO = """【故事背景】
顾泽是顾家亲生儿子，出生时被护士狸猫换太子与顾子航身份互换。十八年后真相大白，顾家却选择继续留养养子顾子航，将亲生儿子顾泽视为弃子。
绝望后的顾泽彻底清醒，不再奢求顾家的认可，凭实力在锐星贵族学校逆袭，用成绩和实力打脸顾家，最终成为商业帝国的新贵。

【重要人物关系】
• 顾父：顾家老爷，城府极深，偏向养子顾子航
• 顾母：顾家太太，表面温和，内心同样偏向顾子航
• 顾子航：假少爷，心机深沉，处处针对顾泽
• 顾家大姐/二姐：对顾泽冷淡，视为外人
• 温知予：温父之女，锐星学校学生，聪慧冷静，是顾泽的重要伙伴
• 温父：锐星学校校长，学者气质，与顾家有旧交
• 顾泽小弟：顾泽暗中培养的心腹，38岁，负责情报工作

【世界观设定】
• 顾家：海城顶级豪门，涉及政商两界
• 锐星贵族学校：海城最顶尖的贵族学校，学生非富即贵
• 白家：与顾家相当的豪门世家
• 顾泽流落在外时被海外势力培养，具备超常的商业和战斗能力"""

# ============ 角色映射（角色名 -> MD文件名, 头像文件名）============
# 玩家角色
PLAYER_ROLE = {
    "name": "顾泽",
    "md_file": "顾泽.md",
    "avatar_file": "顾泽.png",
    "is_player": True,
}

# NPC 角色
NPC_ROLES = [
    {"name": "顾子航",        "md_file": "顾子航.md",            "avatar_file": "顾子航.png"},
    {"name": "顾铭远(顾父)",  "md_file": "顾铭远(顾父).md",      "avatar_file": "顾父.png"},
    {"name": "林雅芝(顾母)",  "md_file": "林雅芝(顾母).md",      "avatar_file": "顾母.png"},
    {"name": "顾念瑶(大姐)",  "md_file": "顾念瑶(大姐).md",      "avatar_file": "顾家大姐.png"},
    {"name": "顾念卿(二姐)",  "md_file": "顾念卿(二姐).md",      "avatar_file": "顾家二姐.png"},
    {"name": "顾家下人",      "md_file": "顾家下人.md",          "avatar_file": "顾家下人.png"},
    {"name": "温知予",        "md_file": "温知予.md",            "avatar_file": "温知予.png"},
    {"name": "温建业",        "md_file": "温建业.md",            "avatar_file": "温父.png"},
    {"name": "陈浩(顾泽手下)", "md_file": "陈浩(顾泽手下).md",    "avatar_file": "顾泽小弟.png"},
    {"name": "白诗韵",        "md_file": "白诗韵.md",            "avatar_file": "白家千金.png"},
    {"name": "路人甲",        "md_file": "路人甲.md",            "avatar_file": "路人甲.png"},
]


def parse_role_md(md_path):
    """解析 Toonflow 角色 MD 文件，提取所有信息"""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    result = {}

    # 提取参数卡 JSON
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    if json_match:
        try:
            result["param_card"] = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            result["param_card"] = {}

    # 提取角色设定文本（## 角色设定 到 ## 角色参数卡 之间）
    setting_match = re.search(
        r"## 角色设定.*?\n(.*?)(?=## 角色参数卡|$)", content, re.DOTALL
    )
    if setting_match:
        result["setting_text"] = setting_match.group(1).strip()

    # 提取头像描述
    avatar_match = re.search(
        r"## 头像.*?\n(.*?)(?=## 语音|$)", content, re.DOTALL
    )
    if avatar_match:
        result["avatar_prompt"] = avatar_match.group(1).strip()

    # 提取语音提示词
    voice_match = re.search(r"- \*\*提示词\*\*：(.+?)$", content, re.MULTILINE)
    if voice_match:
        result["voice_prompt"] = voice_match.group(1).strip()

    # 提取角色类型
    result["is_player"] = "playerRole" in content or "玩家角色" in content

    return result


def build_v2_card(role_name, parsed, is_player=False):
    """将解析的角色数据转换为 SillyTavern V2 角色卡格式"""
    card = parsed.get("param_card", {})

    # 构建 description（核心人设描述）
    desc_parts = []
    if card.get("raw_setting"):
        desc_parts.append(card["raw_setting"])

    setting_text = parsed.get("setting_text", "")
    if setting_text:
        # 去掉参数卡 JSON 块，只保留文本
        setting_clean = re.sub(r"```json.*?```", "", setting_text, flags=re.DOTALL).strip()
        if setting_clean:
            desc_parts.append(setting_clean)

    description = "\n\n".join(desc_parts) if desc_parts else card.get("raw_setting", "")

    # 构建 personality
    personality = card.get("personality", "")

    # 构建 first_mes（开场白）
    if is_player:
        first_mes = (
            '*你打开AI漫剧App观看《破局-从冷落走到瞩目》，突然电闪雷鸣，你头胀目眩。*\n\n'
            '*醒来后，你发现自己在一辆黑色轿车里面。大脑突然涌入陌生的记忆——'
            '原来，你是顾家被遗弃的亲生儿子，在海外摸爬滚打十八年，'
            '创立了黑龙金融集团，资产千亿。*\n\n'
            '*轿车缓缓驶入一座豪华别墅的大门，门楣上挂着\u201c顾宅\u201d二字。*\n\n'
            '司机: 少爷，到了。'
        )
    else:
        first_mes = build_first_mes(role_name, card)

    # 构建 mes_example（对话示例）
    mes_example = build_mes_example(role_name, card, is_player)

    # 构建 tags
    tags = []
    if is_player:
        tags = ["主角", "玩家角色", "逆袭", "都市"]
    else:
        tags = ["NPC", "都市"]
        if "顾" in role_name:
            tags.append("顾家")
        if "温" in role_name:
            tags.append("温家")
        if "白" in role_name:
            tags.append("白家")

    # 构建 V2 卡片
    v2_card = {
        "spec": "chara_card_v2",
        "spec_version": "2.0",
        "data": {
            "name": role_name,
            "description": description,
            "personality": personality,
            "scenario": SCENARIO,
            "first_mes": first_mes,
            "mes_example": mes_example,
            "alternate_greetings": [],
            "character_book": None,
            "tags": tags,
            "creator": "Toonflow",
            "character_version": "1.0",
            "extensions": {
                "toonflow": {
                    "raw_setting": card.get("raw_setting", ""),
                    "gender": card.get("gender", ""),
                    "age": card.get("age", 0),
                    "level": card.get("level", 1),
                    "level_desc": card.get("level_desc", ""),
                    "appearance": card.get("appearance", ""),
                    "voice_prompt": parsed.get("voice_prompt", ""),
                    "avatar_prompt": parsed.get("avatar_prompt", ""),
                    "skills": card.get("skills", []),
                    "items": card.get("items", []),
                    "equipment": card.get("equipment", []),
                    "hp": card.get("hp", 100),
                    "mp": card.get("mp", 50),
                    "money": card.get("money", 0),
                    "other": card.get("other", []),
                    "exp": card.get("exp", 0),
                    "next_level_exp": card.get("next_level_exp", 100),
                    "is_player": is_player,
                }
            },
        },
    }

    return v2_card


def build_first_mes(role_name, card):
    """根据角色生成开场白"""
    level_desc = card.get("level_desc", "")
    personality = card.get("personality", "")
    appearance = card.get("appearance", "")

    # 根据角色定制开场白
    first_mes_map = {
        "顾子航": "*顾子航站在顾家别墅的走廊上，阳光透过落地窗洒在他身上，他脸上挂着温和的笑容，眼睛却暗暗打量着刚走进门的你。*\n\n*他快步走上前，伸出手，语气热情而亲切：*\n\n\"你就是刚回来的弟弟吧？我是顾子航，你的……哥哥。以后我们就是一家人了，有什么需要尽管跟我说。\"\n\n*他的笑容完美无缺，但你总觉得那双眼睛里藏着什么。*",
        "顾铭远(顾父)": "*顾家客厅里，顾铭远端坐在沙发上，手里端着一杯茶。他看了你一眼，目光像在评估一件商品的价值。*\n\n\"回来了。\"\n\n*他的声音平淡，既没有惊喜也没有厌恶，像是在确认一笔投资的回报率。*\n\n\"先去收拾一下，晚上一家人一起吃饭。你的房间已经安排好了。\"\n\n*他没有起身，只是摆了摆手示意你可以走了。*",
        "林雅芝(顾母)": "*林雅芝站在楼梯口，双手不安地绞在一起。她看到你的那一刻，眼神闪过一丝复杂——有愧疚、有慌张，但很快被掩盖过去。*\n\n\"孩子……路上辛苦了吧？\"\n\n*她的声音有些颤抖，走上前来，似乎想要触碰你，但手伸到一半又缩了回去。*\n\n\"你的房间……我已经让人收拾好了。有什么不习惯的跟妈说。\"\n\n*她叫你\"孩子\"时的语气，像是在叫一个陌生人。*",
        "顾念瑶(大姐)": "*顾念瑶靠在客厅的柱子上，双手抱胸，居高临下地看着你。她的眼神冷漠，嘴角带着一丝不屑。*\n\n\"所以你就是那个被找回来的？\"\n\n*她轻笑一声，拨了拨头发。*\n\n\"我不管你以前在外面过的是什么日子，到了顾家，就别给顾家丢人。子航在这个家待了十八年，他才是真正的顾家人。你……好自为之吧。\"\n\n*说完她转身就走了，高跟鞋踩在大理石地面上，发出清脆的声响。*",
        "顾念卿(二姐)": "*顾念卿从二楼走下来，看到你时露出一副\"好心\"的表情。她走到你身边，压低声音说：*\n\n\"弟弟，姐姐提醒你一句——在这个家，要懂得看人脸色。子航哥才是爸妈的心头肉，你刚回来，别太张扬了。\"\n\n*她说着\"为你好\"的话，但嘴角那抹若有若无的笑意，让你觉得事情没那么简单。*\n\n\"当然了，如果你有什么需要，也可以来找姐姐。\"\n\n*她的\"好意\"里，分明藏着算计。*",
        "顾家下人": "*顾家管家快步迎上来，微微鞠躬。他的表情谦卑，但眼神中闪过一丝难以察觉的复杂。*\n\n\"少爷，老爷和夫人们都在客厅等您。请跟我来。\"\n\n*他引着你穿过奢华的门厅，脚步声中规中矩。经过走廊时，他忽然压低声音，飞快地说了一句：*\n\n\"……少爷，欢迎回家。\"\n\n*那语气里，似乎藏着你听不懂的深意。*",
        "温知予": "*锐星贵族学校的走廊上，温知予靠在栏杆旁，阳光洒在她身上，像一幅画。她看到你走来，目光在你身上停留了一瞬。*\n\n\"你是新来的转学生？\"\n\n*她的声音清冷，不带多余的情绪，但那双眼睛像是在审视你的灵魂。*\n\n\"我叫温知予。这个学校的水很深，你最好小心一点。\"\n\n*说完她转身就走，长发在风中飘动，留给你一个高冷的背影。*",
        "温建业": "*温建业坐在校长办公室里，桌上摆着你的转学档案。他摘下眼镜，揉了揉鼻梁，看着你。*\n\n\"你就是顾家新找回来的孩子？\"\n\n*他的语气沉稳，不偏不倚。*\n\n\"锐星学校不看重家世，只看重实力。你能进这所学校，说明你有自己的本事。好好学，别让人看扁了。\"\n\n*他重新戴上眼镜，低头继续批文件，像是在结束一场再普通不过的谈话。*",
        "陈浩(顾泽手下)": "*一辆黑色SUV停在路边，车窗降下，露出一张沉稳的中年男人的脸。他看到你，立刻下车，微微点头。*\n\n\"泽哥，一切按计划进行。顾家的底细我已经查得差不多了。\"\n\n*他递过来一个加密手机，声音压得很低。*\n\n\"另外，锐星学校那边的情况我也摸清了。顾子航在学校里拉了个'少爷团'，专门打压看不顺眼的人。您小心。\"\n\n*说完他重新上车，消失在车流中，像从未出现过一样。*",
        "白诗韵": "*学校食堂里，白诗韵端着餐盘走过你身边，扫了你一眼，嗤笑一声。*\n\n\"你就是顾家那个'找回来'的真少爷？看着也不怎么样嘛。\"\n\n*她旁边几个女生跟着笑起来。白诗韵拨了拨头发，语气高傲：*\n\n\"我劝你离子航远点。他可是这个学校的核心人物，你一个刚来的转学生，别不自量力。\"\n\n*说完她带着人扬长而去，留下食堂里窃窃私语的目光。*",
        "路人甲": "*一个普通的路人从你身边经过，看了你一眼，又匆匆低头赶路。*\n\n*在这个城市里，每个人都有自己的故事，每个人都是别人故事里的配角。但有时候，一个小人物的只言片语，可能藏着改变一切的关键信息。*",
    }

    return first_mes_map.get(role_name, f"*{role_name}出现在你的面前。*\n\n\"{card.get('raw_setting', '')}\"")


def build_mes_example(role_name, card, is_player=False):
    """根据角色生成对话示例"""
    personality = card.get("personality", "")
    setting = card.get("raw_setting", "")

    examples = {
        "顾子航": '{{user}}: 你为什么要针对我？\n{{char}}: *顾子航露出无辜的笑容，双手一摊* "针对？弟弟你说什么呢，我可是你最亲的哥哥啊。"\n*他的眼神闪过一丝冷意，但转瞬即逝* "是这个家的人对你不好吧？你跟我说，我帮你出头。"\n\n{{user}}: 少装了，我知道你做的事。\n{{char}}: *笑容僵了一瞬，随即眼眶泛红，声音颤抖* "弟弟……你怎么能这样说我？我到底做错了什么……"\n*他的演技天衣无缝，但如果仔细看，那双眼睛里没有一丝泪水*',
        "顾铭远(顾父)": '{{user}}: 爸，我能跟您谈谈吗？\n{{char}}: *顾铭远放下手中的文件，抬眼看你* "谈什么？如果是感情上的事，我没兴趣。如果是生意上的事，说。"\n\n{{user}}: 我想进入顾氏集团实习。\n{{char}}: *他冷笑一声* "顾氏集团不是慈善机构。你先在锐星学校证明自己，再谈别的。"\n*他重新拿起文件，语气淡漠* "没有价值的人，没有资格谈条件。"',
        "温知予": '{{user}}: 你为什么愿意帮我？\n{{char}}: *温知予看了你一眼，语气平淡* "我没有在帮你。我只是看到了一个值得投资的人。"\n\n*她顿了顿，目光移向窗外* "这个学校里，大部分人都是靠家世。你是少数靠实力站在这里的人。"\n\n{{user}}: 所以你是在下注？\n{{char}}: *她嘴角微微上扬，算是一个笑* "你可以这么理解。不过我很少看走眼。"',
    }

    if role_name in examples:
        return examples[role_name]

    # 通用示例
    return f'{{{{user}}}}: 你好。\n{{{{char}}}}: *{role_name}看了你一眼* "{setting[:50]}..."'


def embed_card_to_png(png_path, v2_card, output_path):
    """将 V2 角色卡 JSON 嵌入 PNG 的 tEXt chunk
    
    PNG tEXt chunk 标准格式:
      keyword\\x00compression_method\\x00text
    其中 compression_method=0 表示不压缩
    """
    # 编码 JSON 为 base64
    json_str = json.dumps(v2_card, ensure_ascii=False)
    b64_encoded = base64.b64encode(json_str.encode("utf-8"))
    
    # 构建 tEXt chunk data: keyword\x00compression_method\x00text
    keyword = b"chara"
    compression_method = b"\x00"  # 0 = uncompressed
    text_data = b64_encoded
    
    chunk_data = keyword + b"\x00" + compression_method + text_data
    
    # 计算 CRC32
    chunk_type = b"tEXt"
    crc_data = chunk_type + chunk_data
    crc = zlib.crc32(crc_data) & 0xffffffff
    
    # 打包 chunk: length(4) + type(4) + data + crc(4)
    chunk = struct.pack(">I", len(chunk_data)) + chunk_type + chunk_data + struct.pack(">I", crc)
    
    # 读取原始 PNG
    with open(png_path, "rb") as f:
        original_data = f.read()
    
    # 验证 PNG 签名
    png_signature = bytes([137, 80, 78, 71, 13, 10, 26, 10])
    if original_data[:8] != png_signature:
        raise ValueError(f"不是有效的 PNG 文件: {png_path}, 签名={original_data[:8].hex()}")
    
    signature = original_data[:8]
    
    # 解析所有 chunks，找到 IEND
    pos = 8
    chunks = []
    while pos < len(original_data):
        length = struct.unpack(">I", original_data[pos:pos+4])[0]
        chunk_type = original_data[pos+4:pos+8]
        chunk_data = original_data[pos+8:pos+8+length]
        chunk_crc = original_data[pos+8+length:pos+12+length]
        chunks.append((length, chunk_type, chunk_data, chunk_crc))
        pos += 12 + length
        
        if chunk_type == b"IEND":
            break
    
    # 构建新 PNG: signature + 保留所有原始 chunks（但跳过原有的 tEXt） + 新的 tEXt + IEND
    new_png = signature
    
    for length, chunk_type, chunk_data, chunk_crc in chunks:
        if chunk_type == b"tEXt":
            # 跳过原有的 tEXt chunk（我们会添加新的）
            continue
        
        # 重新计算 CRC（以防数据被修改）
        crc_data = chunk_type + chunk_data
        crc = zlib.crc32(crc_data) & 0xffffffff
        new_chunk = struct.pack(">I", length) + chunk_type + chunk_data + struct.pack(">I", crc)
        new_png += new_chunk
        
        if chunk_type == b"IEND":
            # 在 IEND 之前插入新的 tEXt chunk
            new_png = new_png[:-12] + chunk + new_png[-12:]
    
    # 写入输出文件
    with open(output_path, "wb") as f:
        f.write(new_png)
    
    return output_path


def main():
    print("=" * 60)
    print("Toonflow → SillyTavern V2 角色卡转换器")
    print("=" * 60)

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n输出目录: {OUTPUT_DIR}")

    all_roles = [PLAYER_ROLE] + NPC_ROLES
    success_count = 0
    fail_count = 0

    for role in all_roles:
        role_name = role["name"]
        md_path = ROLES_DIR / role["md_file"]
        avatar_path = AVATARS_DIR / role["avatar_file"]
        is_player = role.get("is_player", False)

        print(f"\n--- 处理: {role_name} ---")

        # 检查文件是否存在
        if not md_path.exists():
            print(f"  ✗ MD 文件不存在: {md_path}")
            fail_count += 1
            continue

        if not avatar_path.exists():
            print(f"  ✗ 头像文件不存在: {avatar_path}")
            fail_count += 1
            continue

        # 解析 MD 文件
        parsed = parse_role_md(md_path)
        if not parsed.get("param_card"):
            print(f"  ✗ 未找到参数卡 JSON")
            fail_count += 1
            continue

        # 构建 V2 卡片
        v2_card = build_v2_card(role_name, parsed, is_player)

        # 输出 JSON 文件
        json_path = OUTPUT_DIR / f"{role_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(v2_card, f, ensure_ascii=False, indent=2)
        print(f"  ✓ JSON: {json_path.name}")

        # 嵌入 PNG
        png_path = OUTPUT_DIR / f"{role_name}.png"
        try:
            embed_card_to_png(avatar_path, v2_card, png_path)
            print(f"  ✓ PNG:  {png_path.name}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ PNG 嵌入失败: {e}")
            fail_count += 1

    # 生成索引文件
    index_path = OUTPUT_DIR / "INDEX.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# 破局-从冷落走到瞩目 - 角色卡仓库\n\n")
        f.write(f"共 {len(all_roles)} 个角色卡（SillyTavern V2 格式）\n\n")
        f.write("| 角色名 | 类型 | PNG | JSON |\n")
        f.write("|--------|------|-----|------|\n")
        for role in all_roles:
            name = role["name"]
            rtype = "玩家" if role.get("is_player") else "NPC"
            png_ok = (OUTPUT_DIR / f"{name}.png").exists()
            json_ok = (OUTPUT_DIR / f"{name}.json").exists()
            f.write(f"| {name} | {rtype} | {'✅' if png_ok else '❌'} | {'✅' if json_ok else '❌'} |\n")
        f.write("\n## 使用方法\n\n")
        f.write("### 导入 SillyTavern\n")
        f.write("1. 将 `.png` 文件拖入 SillyTavern 的 `characters/` 目录\n")
        f.write("2. 刷新角色列表即可使用\n")
        f.write("3. PNG 内嵌了完整的 V2 角色卡数据（tEXt chunk, keyword=chara）\n\n")
        f.write("### 导入其他平台\n")
        f.write("- `.json` 文件可直接导入支持 V2 格式的平台（RisuAI、TavernAI 等）\n")
        f.write("- `.png` 文件兼容所有支持 SillyTavern 角色卡的平台\n\n")
        f.write("### 规范信息\n")
        f.write("- 格式: `chara_card_v2` (spec_version 2.0)\n")
        f.write("- 嵌入方式: PNG tEXt chunk, keyword=`chara`, value=base64(UTF-8 JSON)\n")
        f.write("- Toonflow 原始数据保存在 `extensions.toonflow` 字段\n")

    print(f"\n{'=' * 60}")
    print(f"完成！成功 {success_count} 个，失败 {fail_count} 个")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"索引文件: {index_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
