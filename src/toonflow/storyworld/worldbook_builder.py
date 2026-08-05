"""
世界书 MD → worldbook.json 构建器

把 worldbook/ 目录下的所有 .md 文件解析为 worldbook.json。

用法:
    python -m src.cli toonflow worldbook-build --story 谁让这个山大王修仙的

或直接:
    python src/toonflow/storyworld/worldbook_builder.py "D:/Users/.../谁让这个山大王修仙的"
"""
import json
import re
from pathlib import Path


def parse_md_entry(text: str) -> list[dict]:
    """
    解析一个 MD 文件，返回 entries 列表。
    """
    entries = []

    # 按 ## 拆分条目
    parts = re.split(r"\n## ", "\n" + text)

    for part in parts:
        if not part.strip():
            continue

        # 第一部分（parts[0]）是文件头，跳过
        part_stripped = part.strip()
        if not part_stripped:
            continue

        # 去掉 ## 前缀，取标题行
        title_line = part_stripped.split("\n")[0].replace("##", "").strip()

        # 标题：截断到第一个空格+短横线之前
        # 支持格式：## 标题（副标题）- 说明  或  ## 标题 - 说明
        title = re.split(r"\s+[-–]\s+", title_line, maxsplit=1)[0].strip()

        if not title:
            continue

        entry = {
            "title": title,
            "keys": [],
            "constant": False,
            "probability": 100,
            "order": 500,
            "group": None,
            "selectiveLogic": None,
            "selectiveKeys": None,
            "content": "",
        }

        # 解析各字段
        content_lines = []
        in_content = False
        all_lines = part_stripped.split("\n")

        for line in all_lines[1:]:  # 跳过标题行
            line_stripped = line.strip()

            # Content 块：> 开头
            if line_stripped.startswith(">"):
                in_content = True
                content_text = line_stripped.lstrip(">").strip()
                content_lines.append(content_text)
                continue

            # 空行且在 content 里，继续（不中断）
            if not line_stripped and in_content:
                continue

            # 遇到非 > 开头，content 结束
            if in_content and not line_stripped.startswith(">"):
                in_content = False

            if in_content:
                continue

            # 解析字段
            if "**Keys**" in line_stripped or "**Keys（关键词）**" in line_stripped:
                keys_match = re.search(r'`(\[.*?\])`', line_stripped)
                if keys_match:
                    try:
                        entry["keys"] = json.loads(keys_match.group(1))
                    except:
                        pass
            elif "**Constant**" in line_stripped or "**常驻**" in line_stripped:
                entry["constant"] = "true" in line_stripped.lower()
            elif "**Probability**" in line_stripped or "**概率**" in line_stripped:
                prob_match = re.search(r'\d+', line_stripped)
                if prob_match:
                    entry["probability"] = int(prob_match.group())
            elif "**Order**" in line_stripped or "**顺序**" in line_stripped:
                order_match = re.search(r'\d+', line_stripped)
                if order_match:
                    entry["order"] = int(order_match.group())
            elif "**Group**" in line_stripped:
                group_match = re.search(r'\d+|null', line_stripped)
                if group_match and group_match.group() != "null":
                    entry["group"] = int(group_match.group())
            elif "**Selective Logic**" in line_stripped or "**Selective**" in line_stripped:
                logic_match = re.search(r'`(AND ANY|AND ALL|NOT ANY|NOT ALL)`', line_stripped)
                if logic_match:
                    entry["selectiveLogic"] = logic_match.group(1)
            elif "**Selective Keys**" in line_stripped:
                sk_match = re.search(r'`(\[.*?\])`', line_stripped)
                if sk_match:
                    try:
                        entry["selectiveKeys"] = json.loads(sk_match.group(1))
                    except:
                        pass

        # 组合 content
        entry["content"] = "\n\n".join(content_lines)

        # 跳过空 content
        if not entry["content"].strip():
            continue

        entries.append(entry)

    return entries


# 分类映射
CATEGORY_MAP = {
    "_constants.md": "worldConstants",
    "_system.md": "worldSystem",
    "_talent.md": "worldTalent",
    "_atmosphere.md": "worldAtmosphere",
    "_dynamic_wealth.md": "worldDynamicWealth",
    "_progress.md": "worldProgress",
    "world.md": "worldGeography",
    "locations.md": "worldLocations",
    "characters.md": "worldCharacters",
    "factions.md": "worldFactions",
    "items.md": "worldItems",
    "events.md": "worldEvents",
    "random.md": "worldRandom",
}


def build_worldbook(story_dir: str) -> dict:
    """把 story_dir/worldbook/ 下所有 .md 文件构建为 worldbook.json。"""
    wb_dir = Path(story_dir) / "worldbook"
    if not wb_dir.exists():
        raise FileNotFoundError(f"世界书目录不存在: {wb_dir}")

    all_entries = []

    for md_file in sorted(wb_dir.glob("*.md")):
        if md_file.name == "README.md":
            continue

        category = CATEGORY_MAP.get(md_file.name, "worldOther")

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        entries = parse_md_entry(content)

        for entry in entries:
            entry["category"] = category

        all_entries.extend(entries)
        print(f"  {md_file.name}: {len(entries)} 条")

    # 按 Order 排序
    all_entries.sort(key=lambda e: e["order"])

    return {
        "name": wb_dir.parent.name,
        "version": "1.0.0",
        "totalEntries": len(all_entries),
        "entries": all_entries,
    }


def build_and_save(story_dir: str):
    """构建并保存 worldbook.json"""
    wb_dir = Path(story_dir) / "worldbook"
    story_name = wb_dir.parent.name

    print(f"构建世界书: {story_name}")
    print("=" * 50)

    data = build_worldbook(story_dir)

    out_path = wb_dir / "worldbook.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"  总条目: {data['totalEntries']}")
    print(f"  保存到: {out_path}")

    # 统计
    categories = {}
    for e in data["entries"]:
        cat = e.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    print("  分类统计:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat}: {count}")

    return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        story_dir = sys.argv[1]
    else:
        story_dir = input("请输入故事目录路径: ").strip()

    build_and_save(story_dir)
