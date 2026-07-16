"""
MD 文件解析器：角色 MD、章节 MD

角色 MD 格式（Toonflow 标准）:
    # 角色名
    ## 角色设定(性别,年龄,性格,...)
    <文本设定>
    ## 角色参数卡
    ```json
    { "name": "...", "raw_setting": "...", ... }
    ```
    ## 头像(ai生图形象描述)
    - **前景**：...
    - **背景**：...
    ## 语音
    - **模式**：prompt_voice
    - **提示词**：...

章节 MD 格式:
    # 章节标题
    > 成功条件：...
    ## 章节内容
    ```...```
    @旁白：开场白
    ### 小事件
    @角色名：台词
"""
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedRole:
    """解析后的角色数据"""
    name: str = ""
    description: str = ""
    avatar_image_prompt: str = ""
    avatar_bg_prompt: str = ""
    voice_mode: str = "prompt_voice"
    voice_prompt_text: str = ""
    parameter_card: dict = None
    is_player: bool = False
    # 完整的设定文本（## 角色设定 到 ## 角色参数卡 之间）
    setting_text: str = ""


@dataclass
class ParsedChapter:
    """解析后的章节数据"""
    title: str = ""
    content: str = ""
    background_prompt: str = ""
    opening_role: str = "旁白"
    opening_text: str = ""
    completion_condition: str = ""


def parse_role_md(md_path: Path, role_type: str = "npc", forced_name: str = None) -> ParsedRole:
    """
    解析角色 MD 文件，提取所有信息

    Args:
        md_path: MD 文件路径
        role_type: "npc" 或 "player"
        forced_name: 强制角色名（优先使用）
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    result = ParsedRole()
    result.is_player = role_type == "player"

    # 提取名称
    if forced_name:
        result.name = forced_name
    else:
        # 优先从参数卡 JSON 提取
        name_match = re.search(r"- \*\*名称\*\*[：:]\s*(.+)", content)
        if name_match:
            result.name = name_match.group(1).strip()
        if not result.name:
            name_match = re.search(r"^#\s*(.+)", content, re.MULTILINE)
            if name_match:
                result.name = name_match.group(1).strip()

    # 提取参数卡 JSON
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    if json_match:
        try:
            result.parameter_card = json.loads(json_match.group(1))
            # 从参数卡补充名称
            if not result.name and result.parameter_card.get("name"):
                result.name = result.parameter_card["name"]
        except json.JSONDecodeError:
            result.parameter_card = {}

    # 提取角色设定文本（## 角色设定 到 ## 角色参数卡 之间）
    setting_match = re.search(
        r"## 角色设定.*?\n(.*?)(?=## 角色参数卡|## 头像|$)", content, re.DOTALL
    )
    if setting_match:
        result.setting_text = setting_match.group(1).strip()

    # 提取描述（优先从设定文本，降级到参数卡的 raw_setting）
    if result.setting_text:
        result.description = result.setting_text
    elif result.parameter_card and result.parameter_card.get("raw_setting"):
        result.description = result.parameter_card["raw_setting"]

    # 提取头像生图描述
    avatar_match = re.search(
        r"## 头像.*?\n(.*?)(?=## 语音|$)", content, re.DOTALL
    )
    if avatar_match:
        avatar_section = avatar_match.group(1)
        fg_match = re.search(r"\*\*前景\*\*[：:]\s*(.+?)(?=\n\s*[-*]|\n##|\Z)", avatar_section, re.DOTALL)
        if fg_match:
            result.avatar_image_prompt = fg_match.group(1).strip()
        bg_match = re.search(r"\*\*背景\*\*[：:]\s*(.+)", avatar_section, re.DOTALL)
        if bg_match:
            result.avatar_bg_prompt = bg_match.group(1).strip()

    # 提取语音提示词
    voice_match = re.search(r"- \*\*提示词\*\*[：:]\s*(.+?)$", content, re.MULTILINE)
    if voice_match:
        result.voice_prompt_text = voice_match.group(1).strip()

    # 检测是否是玩家角色
    if "玩家角色" in content or "playerRole" in content:
        result.is_player = True

    return result


def parse_chapter_md(md_path: Path) -> ParsedChapter:
    """解析章节 MD 文件"""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    chapter = ParsedChapter()

    # 提取标题
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if title_match:
        chapter.title = title_match.group(1).strip()

    # 提取成功条件
    condition_match = re.search(r"^>\s*成功条件[：:]\s*(.+)", content, re.MULTILINE)
    if condition_match:
        chapter.completion_condition = condition_match.group(1).strip()

    # 提取背景图提示词
    bg_match = re.search(r"^## 章节背景图\s*\n提示词\s*\n```\s*(.+?)\s*```", content, re.DOTALL | re.MULTILINE)
    if bg_match:
        chapter.background_prompt = bg_match.group(1).strip()

    # 提取章节内容（## 章节内容 ``` ... ``` 格式）
    content_match = re.search(r"^## 章节内容\s*\n```\s*(.*?)\s*```", content, re.DOTALL | re.MULTILINE)
    if content_match:
        chapter.content = content_match.group(1).strip()
    else:
        # 降级：提取正文内容（去掉非事件部分）
        content_only = re.sub(r"## 非事件.*", "", content, flags=re.DOTALL)
        lines = content_only.split("\n")
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith(">") or line.startswith("```"):
                continue
            if not line:
                continue
            clean_lines.append(line)
        chapter.content = "\n".join(clean_lines)

    # 提取开场白
    narrator_match = re.search(r"@旁白[：:]\s*(.+?)(?=\n@|\n##|\Z)", content, re.DOTALL)
    if narrator_match:
        chapter.opening_text = narrator_match.group(1).strip()[:200]

    return chapter