"""
下载 Toonflow 服务器上某个世界的全部数据到本地目录。

用法:
    python -m src.toonflow.download_world --world-id 41 \
        --out "ai_story/171/谁让这个山大王修仙的/toonflow_agme_chace"

下载内容:
    1. world.json            —— 故事完整 JSON 数据（世界/settings/playerRole/narratorRole）
    2. worldbook.json        —— 世界书条目（listWorldBook，可能为空）
    3. chapters/             —— 每个章节的 JSON + Markdown 内容 + 背景图
    4. avatars/<角色>/       —— 每个角色的头像三件套（原图/背景图/头像）+ 音色 wav
    5. images/world_cover.*  —— 世界封面图
"""
import argparse
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

# ---------- 配置加载 ----------
_env = {}
if (ROOT / ".env").exists():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        _env[k.strip()] = v.strip()
BASE = _env["BASE_URL"].rstrip("/")
TOKEN = _env.get("TOKEN", "")


def api(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def http_get(url, binary=True):
    """GET 一个文件（图片/音频）。返回 (bytes, content_type) 或 (None, error)。"""
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read() if binary else r.read().decode("utf-8")
        return data, r.headers.get("Content-Type", "")


def ext_from_path(path, content_type=""):
    if path and "." in Path(path).name:
        e = Path(path).suffix.lower()
        if len(e) <= 5:
            return e
    if "png" in content_type:
        return ".png"
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    if "webp" in content_type:
        return ".webp"
    if "wav" in content_type:
        return ".wav"
    if "mp3" in content_type:
        return ".mp3"
    return ""


_ILLEGAL = re.compile(r'[\\/:*?"<>|]')


def safe_name(s: str) -> str:
    s = _ILLEGAL.sub("_", s).strip().strip(".")
    return s[:80] if s else "untitled"


def download_file(url_path, out_path: Path, label=""):
    """url_path 可以是完整 URL 或服务器相对路径（/1/game/...）。已存在则跳过（断点续传）。"""
    url = url_path if url_path.startswith("http") else f"{BASE}{url_path}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # 先按 url 后缀确定最终文件名，支持断点续传
    ext = ext_from_path(url_path, "")
    final = out_path.with_suffix(ext) if not out_path.suffix else out_path
    if final.exists() and final.stat().st_size > 0:
        print(f"    · 跳过(已存在) {label}: {final.name}")
        return final
    try:
        data, ct = http_get(url)
    except Exception as e:
        print(f"    ✗ 下载失败 [{label}]: {url_path} -> {e}")
        return None
    if data is None:
        return None
    # 若实际 content-type 与 url 后缀不符，以 content-type 为准
    ext2 = ext_from_path(url_path, ct)
    final = out_path.with_suffix(ext2) if not out_path.suffix else out_path
    final.write_bytes(data)
    print(f"    ✓ {label}: {final.name} ({len(data)} bytes)")
    return final


def parse_role(ro):
    if isinstance(ro, str):
        try:
            return json.loads(ro)
        except Exception:
            return {}
    return ro or {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world-id", type=int, default=41)
    ap.add_argument("--out", required=True, help="输出根目录")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"==> 下载世界 worldId={args.world_id} 到 {out}")
    res = api("/game/getWorld", {"worldId": args.world_id})
    if res.get("code") != 200:
        raise SystemExit(f"获取世界失败: {res}")
    world = res["data"]

    # 1) 故事 JSON 数据
    (out / "world.json").write_text(
        json.dumps(world, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✓ world.json (name={world.get('name')!r})")

    settings = world.get("settings")
    if isinstance(settings, str):
        settings = json.loads(settings)

    # 2) 世界书
    wb = api("/game/listWorldBook", {"worldId": args.world_id})
    entries = wb.get("data", {}).get("entries", [])
    (out / "worldbook.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✓ worldbook.json (entries={len(entries)})")

    # 3) 世界封面
    if world.get("coverPath"):
        download_file(world["coverPath"], out / "images" / "world_cover", "世界封面")

    # 4) 角色：NPC + player + narrator
    npc_roles = [parse_role(r) for r in settings.get("roles", [])]
    player_role = parse_role(world.get("playerRole"))
    narrator_role = parse_role(world.get("narratorRole"))

    roles_index = {"npc": [], "player": None, "narrator": None}

    def handle_role(ro, kind):
        if not ro or not ro.get("name"):
            return
        name = ro["name"]
        folder = out / "avatars" / safe_name(name)
        folder.mkdir(parents=True, exist_ok=True)
        local = {}
        # 头像三件套
        if ro.get("avatarSourcePath"):
            p = download_file(ro["avatarSourcePath"], folder / "original", "原图")
            if p:
                local["original"] = str(p.relative_to(out))
        if ro.get("avatarBgPath"):
            p = download_file(ro["avatarBgPath"], folder / "background", "背景图")
            if p:
                local["background"] = str(p.relative_to(out))
        if ro.get("avatarPath"):
            p = download_file(ro["avatarPath"], folder / "avatar", "头像")
            if p:
                local["avatar"] = str(p.relative_to(out))
        # 音色文件
        if ro.get("voiceReferenceAudioPath"):
            p = download_file(ro["voiceReferenceAudioPath"], folder / "voice.wav", "音色")
            if p:
                local["voice"] = str(p.relative_to(out))
        local["voiceGeneratedDownloadUrl"] = ro.get("voiceGeneratedDownloadUrl", "")
        local["voicePromptText"] = ro.get("voicePromptText", ro.get("voice", ""))
        # 保存角色原始 JSON
        (folder / "role.json").write_text(
            json.dumps(ro, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return {"id": ro.get("id"), "name": name, "roleType": ro.get("roleType"), "files": local}

    for r in npc_roles:
        info = handle_role(r, "npc")
        if info:
            roles_index["npc"].append(info)
    if player_role:
        roles_index["player"] = handle_role(player_role, "player")
    if narrator_role:
        roles_index["narrator"] = handle_role(narrator_role, "narrator")

    (out / "roles.json").write_text(
        json.dumps(roles_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    n_voice = sum(1 for r in roles_index["npc"] if r["files"].get("voice"))
    print(f"  ✓ roles.json (NPC={len(roles_index['npc'])}, player={roles_index['player'] is not None}, narrator={roles_index['narrator'] is not None})")

    # 5) 章节
    chapters_dir = out / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    bg_dir = chapters_dir / "backgrounds"
    bg_dir.mkdir(parents=True, exist_ok=True)

    ce_ids = [ce.get("chapterId") for ce in settings.get("chapterExtras", []) if ce.get("chapterId")]
    chapter_ids = []
    seen = set()
    for cid in ce_ids:
        if cid not in seen:
            chapter_ids.append(cid)
            seen.add(cid)
    # 兜底：按 chapterCount 扫描（若 chapterExtras 不全）
    cc = world.get("chapterCount", 0) or 0
    if cc > len(chapter_ids):
        for cid in range(1, cc + 5):
            if cid in seen:
                continue
            cr = api("/game/getChapter", {"chapterId": cid, "worldId": args.world_id})
            if cr.get("code") == 200 and cr.get("data") and cr["data"].get("worldId") == args.world_id:
                chapter_ids.append(cid)
                seen.add(cid)

    for idx, cid in enumerate(chapter_ids, 1):
        cr = api("/game/getChapter", {"chapterId": cid, "worldId": args.world_id})
        if cr.get("code") != 200 or not cr.get("data"):
            print(f"    ✗ 章节 {cid} 获取失败")
            continue
        ch = cr["data"]
        title = ch.get("title") or f"chapter_{cid}"
        base = f"chapter_{idx}_{safe_name(title)}"
        # 完整 JSON
        (chapters_dir / f"chapter_{idx}.json").write_text(
            json.dumps(ch, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # Markdown 内容
        content = ch.get("content") or ""
        (chapters_dir / f"{base}.md").write_text(content, encoding="utf-8")
        # 背景图
        bg = ch.get("backgroundPath") or ch.get("coverPath")
        if bg:
            p = download_file(bg, bg_dir / f"chapter_{idx}", f"章节{idx}背景")
        print(f"    ✓ 章节 {idx}: {title} (content {len(content)} 字)")

    print("\n==> 下载完成。")
    print(f"    世界: {world.get('name')}")
    print(f"    NPC角色: {len(roles_index['npc'])} | 含音色: {n_voice}")
    print(f"    章节: {len(chapter_ids)}")
    print(f"    世界书条目: {len(entries)}")
    print(f"    目录: {out}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
