"""用 Agnes AI 生成故事封面/章节封面/章节背景图"""
import json, os, sys
import requests

API_KEY = "sk-SruZYqTXtU0lCoZsuQ528sahDCJ3L1uttWsG13qqB3ppvcYn"
URL      = "https://api.agnes-ai.cn/v1/images/generations"
MODEL    = "agnes-image-2.5-flash"
OUT_DIR  = "D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/ai_story/android_sj/通天传授-收徒系统/image"

IMAGES = [
    {
        "filename": "story_cover.jpg",
        "size": "2K", "ratio": "16:9",
        "prompt": (
            "玄幻修仙喜剧故事封面。东方玄幻仙侠风格，超宽幅横图。山峰之巅，云雾缭绕，巍峨宗门建筑群若隐若现。"
            "正中央浮现金色半透明「收徒系统」法阵界面，法阵发出柔和金光。宗门山门大匾额上书「大罗宗」三字，金光闪耀。"
            "画面左侧站着一个身穿紫袍玉冠的年轻宗主陆川，手持扫帚，神态淡定从容。"
            "右侧有一条穿着花裤衩的黑狗蹲坐，表情傲然天下。花裤衩在风中飘扬。"
            "画面下方还有白衣女子陈南璇负手而立，冷眼看人，嘴角带着不屑。"
            "整个画面诙谐中带着仙气，色调以紫金云雾为主，带有轻喜剧感。"
            "画面干净，角色清晰可辨，高质量CG插画风格，电影级构图。"
        )
    },
    {
        "filename": "story_coverBg.jpg",
        "size": "2K", "ratio": "16:9",
        "prompt": (
            "大罗宗山门九千级石阶，云雾翻涌，山门巍峨，仙气缭绕。东方玄幻修仙风格，超宽幅横图。"
            "画面前景：石阶尽头站着紫袍玉冠的年轻宗主陆川，肩扛扫帚，正抬头看向天空中金色的「收徒系统」法阵投影，表情淡定中带着一丝意外。"
            "画面氛围感极强，云海翻腾，山门建筑古朴庄严，天边有紫电在云中闪烁，暗示宗主的强大修为。"
            "色调紫金蓝白，光影层次丰富，电影级构图，高质量CG插画风格。"
        )
    },
    {
        "filename": "chapter_1_cover.png",
        "size": "2K", "ratio": "9:16",
        "prompt": (
            "玄幻修仙喜剧风格章节封面插画，第1章「拜师大罗宗」专用。画面中央：巍峨的大罗宗山门耸立云端，"
            "九千级石阶从上而下直入云海。山门匾额「大罗宗」三字清晰醒目，金光环绕。"
            "背景云雾缭绕翻涌，紫电在山巅闪烁，天空中隐约可见金色法阵。"
            "画面下方云海中，一条穿着花裤衩的黑狗小白正叼着一枚玉简，眼神傲然。"
            "色调以紫色、金色、云白为主，庄严中带着奇幻喜剧感。竖版构图，CG插画风格，高质量。"
        )
    },
    {
        "filename": "chapter_1_background.png",
        "size": "2K", "ratio": "16:9",
        "prompt": (
            "大罗宗大殿内部场景。东方玄幻修仙喜剧风格，超宽幅横图。"
            "大殿之上，紫袍宗主陆川端坐主位，手持一卷玉简，递向面前的少年萧肿。"
            "萧肿单手接过玉简，眼皮都没抬，一副不屑一顾的表情。殿角，白衣女子陈南璇负手旁观，冷笑。"
            "角落里，一条穿花裤衩的黑狗小白竖起耳朵，正盯着萧肿手中的玉简，眼神发亮，尾巴微微摇动。"
            "大殿古朴庄严，横梁上刻有「大罗宗」三字，殿外云雾翻涌，天边紫电闪烁。"
            "整体氛围诙谐中带着仙气，喜剧感强。色调紫金暖黄，电影级构图，高质量CG插画。"
        )
    },
    {
        "filename": "chapter_2_cover.png",
        "size": "2K", "ratio": "9:16",
        "prompt": (
            "玄幻修仙喜剧风格章节封面插画，第2章「大罗宗日常」专用。画面中央：后山巨石上，"
            "一条穿着彩色花裤衩的黑狗小白四仰八叉躺在石头上晒太阳，花裤衩在风中飘扬，表情惬意傲然。"
            "石头旁，白衣女子陈南璇双手叉腰，用嫌弃的眼神瞪着小白，嘴里似乎在碎碎念。"
            "远处山石间有药田和丹炉，暗示这里是药堂后山，天空蔚蓝，阳光明媚。"
            "整体色调明媚清新，喜剧感强，Q版可爱风。竖版构图，CG插画风格，高质量。"
        )
    },
    {
        "filename": "chapter_2_background.png",
        "size": "2K", "ratio": "16:9",
        "prompt": (
            "大罗宗后山日常场景，阳光明媚。东方玄幻修仙喜剧风格，超宽幅横图。"
            "后山巨石上，一条穿彩色花裤衩的黑狗小白四仰八叉晒太阳，花裤衩随风飘扬，表情傲然享受。"
            "巨石旁，白衣女子陈南璇双手叉腰，用嫌弃的眼神瞪着小白，似乎在碎碎念。"
            "远处山石间有药田和丹炉，天空蔚蓝，白云悠悠。"
            "整体氛围轻松愉快，喜剧感强，色调明媚清新，阳光金色与蓝天白云交相辉映。"
            "电影级构图，高质量CG插画风格。"
        )
    },
]


def gen_image(item: dict) -> str:
    payload = {
        "model": MODEL,
        "prompt": item["prompt"],
        "size": item["size"],
        "ratio": item["ratio"],
        "extra_body": {"response_format": "url"},
    }
    print(f"  生成: {item['filename']} ...")
    r = requests.post(URL, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    img_url = data["data"][0]["url"]
    print(f"  下载: {img_url}")
    # 下载到本地
    img_data = requests.get(img_url, timeout=60).content
    out_path = os.path.join(OUT_DIR, item["filename"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(img_data)
    print(f"  保存: {out_path} ({len(img_data)//1024}KB)")
    return out_path


if __name__ == "__main__":
    print("=" * 60)
    print("Agnes AI 生图：通天传授-收徒系统")
    print("=" * 60)
    results = []
    for item in IMAGES:
        try:
            path = gen_image(item)
            results.append(path)
        except Exception as e:
            print(f"  ❌ 失败: {e}")
    print(f"\n完成！成功 {len(results)}/{len(IMAGES)} 张")
    for p in results:
        print(f"  {p}")
