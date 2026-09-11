# -*- coding: utf-8 -*-
"""批量调用 mimo-v2.5-tts-voicedesign 生成角色音色 wav（描述无争议的 9 个角色）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mimo_tts import gen_voice

CACHE = r"D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.cache/character/通天传授-收徒系统"

ROLES = {
    "墨老":     "沙哑缓慢的老年男声，说话不紧不慢，有长者气度，说到关键处会咳嗽两声再继续",
    "林惊鸿":   "清冷端肃的女声，气质凛然，字正腔圆，愤怒时字字铿锵有力，被气疯时会破音",
    "柳如烟":   "酥软慵懒的成年女声，尾音上扬，笑意藏在字里行间，语速偏慢，妩媚撩人",
    "玄尘长老": "沉稳的老年男性长者音，德高望重，说话慢条斯理，被离谱言论呛到时会语塞咳嗽",
    "玉玲珑":   "清脆灵动的女声，语速快，明媚张扬，带着『本座当年』的傲气与活力",
    "苏沫":     "柔和温婉的年轻女声，亲切绵软，毒舌时语速明显加快，危险前会平静地倒数",
    "陆川":     "清朗温润的青年男声，从容自信，传功授业时一本正经，被质疑时气定神闲微笑不语",
    "陈南璇":   "清脆灵动的少女音，说话带着强烈的自信，被打脸后语塞转暴躁，关心人时别扭",
    "黑袍使":   "低沉冰冷的男声，字句拖长，阴森压迫感强，怒极反笑，笑声低哑",
}

for role, desc in ROLES.items():
    out = os.path.join(CACHE, role, f"{role}_voice.wav")
    if os.path.exists(out):
        print(f"[SKIP] {role} 已存在 {out}")
        continue
    r = gen_voice(desc, out)
    mark = "OK " if r["ok"] else "FAIL"
    print(f"[{mark}] {role} -> {out} | {r['msg'][:80]}")
    if r.get("final_text"):
        print(f"       final_text: {r['final_text'][:60]}")

print("BATCH DONE")