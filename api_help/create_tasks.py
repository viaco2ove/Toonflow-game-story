import urllib.request, json, time

url = 'http://122.51.232.171:60002/game/saveTask'
token = '***REMOVED***'
chapter_id = 52

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

tasks = [
    {"title": "寻找失踪的同学", "desc": "李明说班上有同学三天前失踪了，帮忙找到他", "goal": "talk_to_npc", "npc": "李明"},
    {"title": "校长的邀请函", "desc": "校长邀请你到办公室聊聊，去还是不去？", "goal": "user_choice", "choices": ["去见校长", "婉拒"]},
    {"title": "半夜的钢琴声", "desc": "每晚午夜，教学楼传来钢琴声，去查看", "goal": "explore", "location": "教学楼"},
    {"title": "小七的日记", "desc": "试图偷看小七的日记，了解她的真实身份", "goal": "stealth", "target": "小七的宿舍"},
    {"title": "食堂的奇怪菜单", "desc": "食堂今天的菜单写着今日特供：新鲜血肉，问问食堂阿姨", "goal": "talk_to_npc", "npc": "路人甲（食堂阿姨）"},
    {"title": "厕所里的第三格", "desc": "男生厕所第三个隔间永远锁着，从里面传出哼歌声音", "goal": "explore", "location": "男生厕所"},
    {"title": "图书馆的禁书区", "desc": "图书馆有一排书被刻意遮挡，尝试取下一本", "goal": "explore", "location": "图书馆"},
    {"title": "校医院的深夜急诊", "desc": "有学生半夜尖叫着跑进校医院，随后安静了", "goal": "investigate", "location": "校医院"},
    {"title": "小七的朋友", "desc": "小七说要介绍朋友给你认识，跟着去", "goal": "follow", "target": "小七"},
    {"title": "运动会的奇怪项目", "desc": "学校运动会有一个项目叫夺旗——旗子插在墓地中央", "goal": "challenge", "location": "学校操场"},
    {"title": "苏老师的课后辅导", "desc": "苏老师单独叫你去办公室辅导功课", "goal": "user_choice", "choices": ["接受辅导", "找借口推辞"]},
    {"title": "找到出口", "desc": "王思远认为学校的后门可能是出口，一起去查看", "goal": "explore", "location": "学校后门"},
    {"title": "无面人的试卷", "desc": "考试时发现无面人满分，但他的试卷上的字迹在蠕动", "goal": "observe", "target": "无面人"},
    {"title": "女生宿舍的敲门声", "desc": "半夜有人敲女生宿舍的门，喊着还我命来", "goal": "explore", "location": "女生宿舍"},
    {"title": "捡到一枚学生证", "desc": "在地上捡到一枚学生证，照片上的人已经没有了脸", "goal": "inspect", "item": "无脸学生证"},
    {"title": "校长的收藏室", "desc": "校长说可以带你看他的收藏，去不去？", "goal": "user_choice", "choices": ["去参观", "不去"]},
    {"title": "帮李明送信", "desc": "李明写了一封信，要你偷偷塞进校长的信箱", "goal": "deliver", "item": "李明的信"},
    {"title": "目击收割", "desc": "亲眼目睹校长对一名学生执行收割仪式", "goal": "witness", "target": "校长"},
    {"title": "小七的警告", "desc": "小七严肃地警告你：不要再去三楼走廊", "goal": "receive_warning", "from": "小七"},
    {"title": "调查发现：影子", "desc": "王思远发现有些学生的影子会自己动，调查此事", "goal": "investigate", "target": "影子现象"},
    {"title": "体育课的自由活动", "desc": "体育课上，老师让学生自由活动——然后学生开始互相追逐撕咬", "goal": "witness", "location": "操场"},
    {"title": "小七的过去", "desc": "趁小七不在，询问其他诡异关于小七的过去", "goal": "talk_to_npc", "npc": "路人甲（老诡异）"},
    {"title": "食堂的地下室", "desc": "食堂阿姨说地下室有新鲜食材，想看看吗？", "goal": "explore", "location": "食堂地下室"},
    {"title": "赵小胖的霉运挑战", "desc": "赵小胖提议打赌：谁能在一小时内不遇到倒霉事", "goal": "challenge", "target": "赵小胖"},
    {"title": "校医院的秘密病历", "desc": "偷偷翻阅校医院的病历本，发现所有学生的入院原因都是精神失常", "goal": "stealth", "location": "校医院"},
    {"title": "音乐教室的琴谱", "desc": "音乐教室有一本琴谱，上面的音符在看不懂的情况下会让人想睡觉", "goal": "inspect", "location": "音乐教室"},
    {"title": "小七教你诡异语", "desc": "小七说如果你想在这所学校生存，需要学一点诡异语", "goal": "learn", "teacher": "小七"},
    {"title": "目击苏老师进食", "desc": "半夜看到苏老师在操场角落进食——那不是人类的食物", "goal": "witness", "target": "苏老师"},
    {"title": "找到校规的完整版", "desc": "墙上贴的校规只有三条，王思远说完整版有三十条", "goal": "collect", "target": "完整校规"},
    {"title": "帮赵小胖找他的零食", "desc": "赵小胖的零食被偷了，帮他找——结果偷零食的是一只诡异老鼠", "goal": "find", "target": "诡异老鼠"},
    {"title": "教室里的第四十三号座位", "desc": "班级只有42个学生，但教室里有43个座位，且第43个座位每天都有不同的名字", "goal": "investigate", "location": "教室"},
    {"title": "校长的茶会", "desc": "校长每周举办一次茶会，被邀请的学生都没有回来", "goal": "user_choice", "choices": ["接受邀请", "拒绝"]},
    {"title": "小七不在的夜晚", "desc": "小七说今晚要出去一下，你偷偷跟着她", "goal": "follow", "target": "小七"},
    {"title": "篮球场上的鬼影", "desc": "半夜篮球场有人打球，过去看看——是已经死去的学生在打球", "goal": "witness", "location": "篮球场"},
    {"title": "帮王思远做实验", "desc": "王思远想测试诡异是否怕光，需要你帮忙当诱饵", "goal": "assist", "partner": "王思远"},
    {"title": "校医院的新药", "desc": "校医院在分发一种新药，吃了会让人的影子消失", "goal": "user_choice", "choices": ["吃下药", "拒绝"]},
    {"title": "小七给你的护身符", "desc": "小七给你一个护身符，说遇到危险就捏碎它", "goal": "receive_item", "item": "小七的护身符"},
    {"title": "图书馆的守夜人", "desc": "图书馆晚上不关门，因为守夜人需要看书", "goal": "meet_npc", "npc": "守夜人"},
    {"title": "调查发现：为什么没有毕业照", "desc": "这所学校似乎从来没有毕业照，调查原因", "goal": "investigate", "target": "学校历史"},
    {"title": "裂口女的提问", "desc": "在三楼走廊被裂口女拦住，她问：我美吗？", "goal": "survive", "threat": "裂口女"},
    {"title": "小七吃的是什么", "desc": "偷偷观察小七吃东西，发现她在吃——和 humans 完全不同的东西", "goal": "witness", "target": "小七"},
    {"title": "校长的家长会", "desc": "校长要举办家长会，但学生的家长都已经……", "goal": "investigate", "location": "学校礼堂"},
    {"title": "找到表妹的照片", "desc": "在学校的相册里找有没有你表妹的照片——结果发现了令人震惊的事实", "goal": "investigate", "location": "学校档案室"},
    {"title": "帮李明守夜", "desc": "李明说今晚它们会来，要你一起守夜", "goal": "survive_night", "partner": "李明"},
    {"title": "游泳课的水下", "desc": "游泳课时，水下有一个人影在向你招手", "goal": "user_choice", "choices": ["潜水查看", "无视"]},
    {"title": "小七生气了", "desc": "你无意间说了一句话，让小七显露出诡异的一面", "goal": "witness", "target": "小七"},
    {"title": "校长的茶", "desc": "校长亲自给你泡了一杯茶，喝还是不喝？", "goal": "user_choice", "choices": ["喝", "不喝"]},
    {"title": "目击诡异开会", "desc": "半夜看到学校的诡异们聚集在礼堂，似乎在讨论如何处理那个异类（用户）", "goal": "witness", "location": "学校礼堂"},
    {"title": "找到离开的方法", "desc": "王思远和李明认为他们找到了离开这所学校的方法", "goal": "escape", "partners": ["王思远", "李明"]},
    {"title": "小七的告白", "desc": "小七在某天晚上，认真看着你，说：其实我不是你的表妹。", "goal": "receive_truth", "from": "小七"},
]

results = []
for i, t in enumerate(tasks, 1):
    data = {
        'chapterId': chapter_id,
        'title': f'{i:03d} - {t["title"]}',
        'taskType': 'side',
        'goalType': 'dialogue',
        'status': 'todo'
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            code = result.get('code')
            tid = result.get('data', {}).get('id', '?')
            print(f'{i:03d} | {code} | taskId={tid} | {t["title"]}')
            results.append({'id': tid, 'title': t['title'], 'code': code})
    except Exception as e:
        print(f'{i:03d} | ERROR: {e} | {t["title"]}')
    time.sleep(0.3)

print('\n=== 完成 ===')
print(f'成功: {sum(1 for r in results if r["code"]==200)}/{len(tasks)}')
if results:
    print('\n任务ID列表（前10个）：')
    for r in results[:10]:
        print(f'  {r["id"]}: {r["title"][:20]}...')
