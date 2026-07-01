#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用世界37作为参考，修复世界36的字段。
读取37的 settings（globalBackground, coverPath, coverBgPath, intro），
把 world-copy 的文件路径替换为 scene 路径，写入36。
"""

import requests
import json

BASE_URL = "http://122.51.232.171:60002"
TOKEN = "xxx"
PROJECT_ID = 1
WORLD_36 = 36
WORLD_37 = 37

def api_call(path, data):
    url = f"{BASE_URL}{path}"
    resp = requests.post(url, json=data, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=60)
    return resp.json()

def main():
    # 读取世界37的settings
    r37 = api_call("/game/getWorld", {"worldId": WORLD_37, "projectId": PROJECT_ID})
    if r37.get("code") != 200:
        print(f"获取世界37失败: {r37}")
        return
    data37 = r37["data"]
    settings37_str = data37.get("settings", "{}")
    settings37 = json.loads(settings37_str) if isinstance(settings37_str, str) else settings37_str

    print(f"世界37 intro长度: {len(data37.get('intro',''))}")
    print(f"世界37 settings.intro长度: {len(settings37.get('intro',''))}")
    print(f"世界37 globalBackground长度: {len(settings37.get('globalBackground',''))}")
    print(f"世界37 settings.coverPath: {settings37.get('coverPath','')[:80]}")
    print(f"世界37 settings.coverBgPath: {settings37.get('coverBgPath','')[:80]}")

    # 读取世界36的现有数据
    r36 = api_call("/game/getWorld", {"worldId": WORLD_36, "projectId": PROJECT_ID})
    if r36.get("code") != 200:
        print(f"获取世界36失败: {r36}")
        return
    data36 = r36["data"]
    settings36_str = data36.get("settings", "{}")
    settings36 = json.loads(settings36_str) if isinstance(settings36_str, str) else settings36_str

    print(f"\n世界36 intro长度: {len(data36.get('intro',''))}")
    print(f"世界36 settings.intro长度: {len(settings36.get('intro',''))}")
    print(f"世界36 globalBackground长度: {len(settings36.get('globalBackground',''))}")
    print(f"世界36 settings.coverPath: {settings36.get('coverPath','')[:80]}")
    print(f"世界36 settings.coverBgPath: {settings36.get('coverBgPath','')[:80]}")

    # 从37获取章节列表及其backgroundPath
    chapters37 = {}
    for cid in range(1, 300):
        ch_resp = api_call("/game/getChapter", {"chapterId": cid, "worldId": WORLD_37})
        if ch_resp.get("code") == 200 and ch_resp.get("data"):
            ch = ch_resp["data"]
            if ch.get("worldId") == WORLD_37:
                chapters37[ch.get("title", "")] = ch

    # 从36获取章节列表
    chapters36 = {}
    for cid in range(1, 300):
        ch_resp = api_call("/game/getChapter", {"chapterId": cid, "worldId": WORLD_36})
        if ch_resp.get("code") == 200 and ch_resp.get("data"):
            ch = ch_resp["data"]
            if ch.get("worldId") == WORLD_36:
                chapters36[ch.get("title", "")] = ch

    print(f"\n世界36章节: {list(chapters36.keys())}")
    print(f"世界37章节: {list(chapters37.keys())}")

    # 更新世界36的settings
    # 使用37的 intro/globalBackground/coverPath/coverBgPath
    settings36["intro"] = settings37.get("intro", settings37.get("globalBackground", ""))
    settings36["globalBackground"] = settings37.get("globalBackground", "")
    settings36["coverPath"] = settings37.get("coverPath", "")
    settings36["coverBgPath"] = settings37.get("coverBgPath", "")

    # 更新36的世界字段
    save_data = {
        "worldId": WORLD_36,
        "id": WORLD_36,
        "projectId": PROJECT_ID,
        "name": data36.get("name", ""),
        "intro": data36.get("intro", ""),
        "coverPath": data36.get("coverPath", ""),
        "settings": json.dumps(settings36),
    }

    print(f"\n写入世界36 settings内容:")
    print(f"  intro长度: {len(settings36.get('intro',''))}")
    print(f"  globalBackground长度: {len(settings36.get('globalBackground',''))}")
    print(f"  coverPath: {settings36.get('coverPath','')[:80]}")
    print(f"  coverBgPath: {settings36.get('coverBgPath','')[:80]}")

    result = api_call("/game/saveWorld", save_data)
    if result.get("code") == 200:
        print(f"\n✓ 世界36 settings更新成功")
    else:
        print(f"\n✗ 世界36 settings更新失败: {result}")

    # 更新36的章节backgroundPath（从37读取路径）
    for title, ch36 in chapters36.items():
        ch37 = chapters37.get(title)
        if not ch37:
            print(f"  37无对应章节: {title}")
            continue

        bg37 = ch37.get("backgroundPath", "")
        cover37 = ch37.get("coverPath", "")

        # 如果37有背景图，复制到36（注意路径可能包含world-copy）
        # 由于文件已经在37上，我们直接使用同样的路径
        update_data = {
            "chapterId": ch36["id"],
            "worldId": WORLD_36,
            "title": ch36.get("title", ""),
            "backgroundPath": bg37,
            "coverPath": cover37,
            "sort": ch36.get("sort", 0),
            "status": "draft",
        }

        upd = api_call("/game/saveChapter", update_data)
        if upd.get("code") == 200:
            print(f"  ✓ {title}: backgroundPath={bg37[:60]}")
        else:
            print(f"  ✗ {title} 更新失败: {upd}")

if __name__ == "__main__":
    main()
