import urllib.request, json

BASE_URL = "http://122.51.232.171:60002"
TOKEN = "***REMOVED***"
WORLD_ID = 35

def api_call(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": 500, "message": str(e)}

# 1. 先获取当前世界数据
print("=== 1. 获取当前世界数据 ===")
world_resp = api_call("/game/getWorld", {"worldId": WORLD_ID})
if world_resp.get("code") != 200:
    print(f"获取世界失败: {world_resp}")
    exit(1)

world_data = world_resp.get("data", {})
settings_str = world_data.get("settings", "{}")
settings = json.loads(settings_str) if isinstance(settings_str, str) else settings_str

# 获取现有角色列表
existing_roles = settings.get("roles", [])
print(f"现有角色数: {len(existing_roles)}")
for r in existing_roles:
    print(f"  - {r.get('name', '?')} ({r.get('id', '?')})")

# 2. 定义所有角色的头像和音色提示词
role_updates = {
    "npc_xiaoqi": {
        "avatarPrompt": "一位黑色长发的少女，齐刘海，浅浅酒窝，嘴角带着温柔笑意，白色校服领口别着一枚黑色发卡，瞳孔隐约泛着竖瞳光泽，二次元动漫风格，半身像，柔和打光，细腻皮肤质感，略带神秘氛围",
        "avatarBgPrompt": "黄昏时分的学校走廊，窗外夕阳余晖洒入，地面有一道微微分裂成两道的影子，氛围温暖中暗藏诡异",
        "voicePromptText": "青年女声，约18-20岁，音色轻柔甜美如邻家妹妹，对'表哥'说话时带着撒娇般的黏人尾音；但语气深处藏着一丝不易察觉的冰冷和非人感，当进入战斗或面对威胁时，声音瞬间变得低沉危险，如同毒蛇吐信，温柔与残忍无缝切换",
    },
    "npc_sulaoshi": {
        "avatarPrompt": "一位容貌艳丽的年轻女性，黑色大波浪卷发，穿着得体的深色职业套装，嘴角挂着温柔迷人的微笑，眼神却深不见底，二次元动漫风格，半身像，精致妆容，优雅气质，美丽外表下暗藏危险气息",
        "avatarBgPrompt": "学校教师办公室，黄昏光线透过百叶窗洒入，墙上挂满优秀学生奖状，办公桌上放着一本翻开的点名册，氛围温馨却令人不安",
        "voicePromptText": "成年女性，约28岁，音色温柔磁性如最善解人意的班主任，语速缓慢优雅，每个字都带着让人卸下防备的魔力；笑声如银铃般悦耳却暗藏寒意，当'辅导'学生时声音会变得黏腻而贪婪，如同蜘蛛在缠绕猎物",
    },
    "npc_xiaozhang": {
        "avatarPrompt": "一位五十多岁的儒雅男士，戴着金丝眼镜，一丝不苟的深色西装，温和而威严的微笑，眼神深邃如潭水，二次元动漫风格，半身像，成熟稳重气质，表面和蔼可亲却暗藏上位者威压",
        "avatarBgPrompt": "学校校长办公室，红木办公桌后是一排书架，墙上挂着学校锦旗和合影，窗外是暮色中的校园，氛围庄重而压抑",
        "voicePromptText": "中年男性，约50岁，音色温和儒雅如德高望重的老校长，语速缓慢沉稳，每个字都透着让人信服的力量；笑声低沉而意味深长，如同看透一切的智者；当谈及'管理学校'时，语气中会闪过一丝冷酷的玩味，如同农场主谈论牲畜",
    },
    "npc_liekounv": {
        "avatarPrompt": "一位身穿红色风衣的女性，长发遮住了大半张脸，只露出裂开到耳根的嘴角和无数尖牙，眼神空洞而疯狂，二次元恐怖动漫风格，半身像，暗红主色调，诡异而令人毛骨悚然的视觉冲击",
        "avatarBgPrompt": "昏暗的学校走廊尽头，一盏闪烁的日光灯下，墙壁斑驳，地面潮湿，远处是深不见底的黑暗，氛围极度压抑恐怖",
        "voicePromptText": "女性，声音忽远忽近如同在走廊中回荡，带着明显的电子失真感；问'我美吗'时语气甜腻如热恋中的少女，但当被回答'不美'时瞬间撕裂成尖锐刺耳的嘶吼，笑声如同玻璃碎裂般令人毛骨悚然",
    },
    "npc_wumianren": {
        "avatarPrompt": "一个穿着校服的少年，脸部是一片光滑无五官的皮肤，头顶裂开一张嘴，露出参差不齐的牙齿，坐姿僵硬，二次元恐怖动漫风格，半身像，灰白主色调，诡异而令人不安的怪异感",
        "avatarBgPrompt": "昏暗的教室角落，课桌上摊开着试卷，周围同学模糊虚化，头顶的日光灯发出惨白光芒，氛围死寂而压抑",
        "voicePromptText": "无面人没有真正的声音，头顶的嘴发出的是混合音——像是把教室里十几个人的声音重叠在一起，有男有女、有老有少，同时说话却说着同样的内容，带着令人不安的共鸣感和机械感，如同坏掉的录音机在重复播放",
    },
    "npc_changfav": {
        "avatarPrompt": "一位黑色超长头发的少女，头发遮住半张脸，只露出一只冰冷的眼睛，身穿白色睡衣，手中握着一把木梳，梳落的头发在地上微微蠕动，二次元恐怖动漫风格，半身像，暗色调，阴森而诡异的美感",
        "avatarBgPrompt": "昏暗的女生宿舍，铁架床、旧衣柜、斑驳的墙壁，窗外月光惨白地照入，地上散落着蠕动的发丝，氛围阴冷而窒息",
        "voicePromptText": "青年女性，音色低沉如从床底或墙壁中传来的细语，带着空洞的回音；说话时伴随着头发摩擦的沙沙声，如同无数蛇在爬行；当发现猎物时声音会变得兴奋而急促，如同饥饿的野兽发现食物，阴森中透着病态的渴望",
    },
    "npc_liming": {
        "avatarPrompt": "一位17岁少年，浓重的黑眼圈，略显脏乱的校服，眼神警惕地扫视四周，像一只受惊的麻雀，二次元动漫风格，半身像，疲惫而紧张的神情，瘦削的脸庞，凌乱的短发",
        "avatarBgPrompt": "学校某个偏僻角落，墙上有奇怪的涂鸦和划痕，光线昏暗，远处传来不明的声响，氛围紧张而压抑",
        "voicePromptText": "17岁少年音，声音发颤带着明显的恐惧，语速急促时断时续，如同受惊的麻雀；说话时会不自觉地压低声音四处张望，呼吸急促，当提到'逃离'或'诡异'时声音会陡然尖锐，透着绝望中的最后一丝希望",
    },
    "npc_wangsiyuan": {
        "avatarPrompt": "一位17岁少年，戴着眼镜，校服整洁，手中拿着笔记本和笔，表情冷静若有所思，眼神中透着理性与分析的光芒，二次元动漫风格，半身像，学霸气质，干净利落的短发，斯文而沉稳",
        "avatarBgPrompt": "学校图书馆一角，书架上摆满书籍，桌上摊开着写满笔记的本子，窗外是黄昏的校园，氛围安静而充满学术气息",
        "voicePromptText": "17岁少年音，声音平静沉稳，语速不快但每个字都经过思考，带着理性分析的味道；即使面对恐怖场景也能保持冷静叙述，偶尔推眼镜时会停顿一下，当发现重要线索时语气中会闪过一丝压抑的兴奋，如同解谜者找到关键拼图",
    },
    "npc_zhaoxiaopang": {
        "avatarPrompt": "一位16岁微胖少年，圆脸，校服被撑得有点紧，脸上挂着憨厚的笑容，嘴角还沾着零食碎屑，二次元动漫风格，半身像，乐观开朗的神情，可爱的圆脸，眯起的眼睛，阳光而单纯",
        "avatarBgPrompt": "学校食堂，桌上散落着零食包装袋，周围同学或惊恐或无奈地看着他，氛围轻松中带着一丝荒诞喜剧感",
        "voicePromptText": "16岁少年音，声音憨厚带着乐观的笑意，即使说着倒霉的事也笑嘻嘻的；说话时偶尔会喘气（因为体型微胖），吃东西时会发出满足的咀嚼声；当遇到危险时声音会陡然拔高变得尖锐，带着惊慌失措的喜剧感，倒霉却又让人忍俊不禁",
    },
    "npc_lurenjia": {
        "avatarPrompt": "一位面容普通的中年人，穿着学校工作人员的制服，表情平淡无奇，没有明显特征，二次元动漫风格，半身像，中性气质，模糊而不起眼的五官，随时可以融入任何场景",
        "avatarBgPrompt": "学校走廊或办公室，背景元素模糊处理，氛围平淡日常，突出其'路人'属性",
        "voicePromptText": "万能角色，音色根据当前扮演身份而变化——扮演食堂阿姨时粗犷热情，扮演宿管时严肃刻板，扮演校医时温柔关切，扮演路人学生时平淡无奇；核心特点是'不引人注意'，声音总是恰到好处地融入环境，不会给玩家留下深刻印象",
    },
    "player": {
        "avatarPrompt": "一位16岁少年，普通学生模样，穿着略显旧色的校服，表情困惑而警觉，眼神中带着误入异世界的不安，二次元动漫风格，半身像，平凡而真实的少年感，黑色短发，清秀但不出众的五官",
        "avatarBgPrompt": "黄昏时分的乡村小路尽头，前方是若隐若现的诡异学校大门，雾气弥漫，氛围神秘而充满未知",
        "voicePromptText": "16岁少年音，清澈略带紧张，普通高中生语气，面对危险时会声音发颤但努力保持冷静",
    },
}

# 3. 更新现有角色或添加新角色
updated_count = 0
added_count = 0

# 创建角色ID到角色的映射
existing_role_map = {r.get("id", ""): r for r in existing_roles}

for role_id, updates in role_updates.items():
    if role_id in existing_role_map:
        # 更新现有角色
        role = existing_role_map[role_id]
        role["avatarPrompt"] = updates["avatarPrompt"]
        role["avatarBgPrompt"] = updates["avatarBgPrompt"]
        role["voicePromptText"] = updates["voicePromptText"]
        # 确保voiceMode设置正确
        if role.get("voiceMode") == "text":
            role["voiceMode"] = "prompt_voice"
        updated_count += 1
        print(f"更新角色: {role.get('name', role_id)}")
    else:
        # 新角色，需要添加到settings.roles
        # 从已知信息推断角色名
        role_name_map = {
            "npc_xiaoqi": "小七",
            "npc_sulaoshi": "苏老师",
            "npc_xiaozhang": "校长",
            "npc_liekounv": "裂口女",
            "npc_wumianren": "无面人",
            "npc_changfav": "长发女",
            "npc_liming": "李明",
            "npc_wangsiyuan": "王思远",
            "npc_zhaoxiaopang": "赵小胖",
            "npc_lurenjia": "路人甲",
            "player": "许飞",
        }
        new_role = {
            "id": role_id,
            "name": role_name_map.get(role_id, role_id),
            "roleType": "player" if role_id == "player" else "npc",
            "avatarPrompt": updates["avatarPrompt"],
            "avatarBgPrompt": updates["avatarBgPrompt"],
            "voiceMode": "prompt_voice",
            "voicePromptText": updates["voicePromptText"],
        }
        existing_roles.append(new_role)
        added_count += 1
        print(f"添加新角色: {new_role['name']}")

# 4. 更新旁白音色
narrator_voice = "混合音色，清朗温润如说书人，讲述恐怖场景时语气沉稳不带波澜，营造反差感；推进剧情时节奏明快，引导用户时亲切自然"
settings["narratorVoice"] = narrator_voice
settings["narratorVoiceMode"] = "prompt_voice"
settings["narratorVoicePromptText"] = narrator_voice

print(f"\n更新旁白音色提示词")

# 5. 保存更新后的世界
print("\n=== 2. 保存更新后的世界 ===")

# 重新构建settings（保持其他字段不变）
settings["roles"] = existing_roles

save_data = {
    "worldId": WORLD_ID,
    "projectId": world_data.get("projectId", 1),
    "name": world_data.get("name", "我的诡异表妹"),
    "intro": world_data.get("intro", ""),
    "settings": settings,
}

# 如果有playerRole和narratorRole，保留它们
if world_data.get("playerRole"):
    player_role = world_data["playerRole"]
    if isinstance(player_role, str):
        player_role = json.loads(player_role)
    # 更新玩家角色的头像和音色
    if "player" in role_updates:
        player_role["avatarPrompt"] = role_updates["player"]["avatarPrompt"]
        player_role["avatarBgPrompt"] = role_updates["player"]["avatarBgPrompt"]
        player_role["voiceMode"] = "prompt_voice"
        player_role["voicePromptText"] = role_updates["player"]["voicePromptText"]
    save_data["playerRole"] = player_role

if world_data.get("narratorRole"):
    narrator_role = world_data["narratorRole"]
    if isinstance(narrator_role, str):
        narrator_role = json.loads(narrator_role)
    narrator_role["voiceMode"] = "prompt_voice"
    narrator_role["voicePromptText"] = narrator_voice
    save_data["narratorRole"] = narrator_role

save_resp = api_call("/game/saveWorld", save_data)
print(f"保存结果: {save_resp.get('code')} - {save_resp.get('message', '无消息')}")

if save_resp.get("code") == 200:
    print(f"\n=== 完成 ===")
    print(f"更新角色: {updated_count}")
    print(f"添加角色: {added_count}")
    print(f"旁白音色: 已更新")
else:
    print(f"\n保存失败详情: {json.dumps(save_resp, ensure_ascii=False, indent=2)}")
