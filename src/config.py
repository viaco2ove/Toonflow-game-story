"""
统一配置加载：全局 .env + 故事 .env + story.json

使用方式:
    from src.config import load_config
    cfg = load_config("破局-从冷落走到瞩目")
    print(cfg.story_name, cfg.world_id, cfg.roles)
"""
import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


def _parse_env_file(env_path: Path) -> dict:
    """手动解析 .env 文件，支持多行值（双引号包裹）"""
    if not env_path.exists():
        return {}

    result = {}
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        if line.strip().startswith("#") or not line.strip() or "=" not in line:
            i += 1
            continue

        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()

        # 多行值（双引号跨行）
        if val.startswith('"') and not val.endswith('"'):
            multi = val[1:]
            i += 1
            while i < len(lines):
                nl = lines[i].rstrip("\n")
                if '"' in nl:
                    idx = nl.index('"')
                    multi += "\n" + nl[:idx]
                    val = multi
                    break
                else:
                    multi += "\n" + nl
                    i += 1
        elif val.startswith('"') and val.endswith('"') and len(val) > 1:
            val = val[1:-1]

        result[key] = val
        i += 1

    return result


def _parse_json_env(val: str, default=None):
    """解析 JSON 格式的环境变量值"""
    if not val:
        return default if default is not None else {}
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


@dataclass
class RoleMapping:
    """单个角色的映射配置"""
    name: str
    md_file: str
    avatar_file: str = ""
    is_player: bool = False


@dataclass
class StoryConfig:
    """故事配置（从 .env + story.json 合并）"""
    story_name: str
    story_dir: Path
    world_id: int = 0
    project_id: int = 1
    intro: str = ""
    global_bg: str = ""

    # 角色映射
    player_role: Optional[RoleMapping] = None
    npc_roles: list = field(default_factory=list)  # list[RoleMapping]

    # 路径
    roles_dir: Path = None
    avatars_dir: Path = None
    chapters_dir: Path = None
    image_dir: Path = None

    # 卡片输出目录
    cards_output_dir: Path = None

    # 章节封面映射 (chapter_index -> {cover, background})
    chapter_covers: dict = field(default_factory=dict)

    # 角色卡场景设定
    card_scenario: str = ""

    # 卡片标签
    card_tags: list = field(default_factory=lambda: ["Roleplay"])


@dataclass
class GlobalConfig:
    """全局配置"""
    # Toonflow 服务器
    base_url: str = "http://localhost:60002"
    token: str = ""
    username: str = "admin"
    password: str = ""

    # chub.ai
    chub_username: str = ""
    chub_password: str = ""
    chub_gateway: str = "https://gateway.chub.ai"
    chub_ro_api: str = "https://ro.chub.ai"

    # cards.sillytavern.one
    cards_base_url: str = "https://cards.sillytavern.one"
    cards_username: str = ""
    cards_password: str = ""

    # 路径
    project_root: Path = None
    ai_story_local_dir: Path = None
    characters_repo_dir: Path = None

    # 头像子目录
    avatars_subdir: str = ""


def load_global_config(project_root: Path = None) -> GlobalConfig:
    """加载全局 .env 配置"""
    if project_root is None:
        project_root = Path(__file__).parent.parent

    env = _parse_env_file(project_root / ".env")

    ai_story_local = env.get("AI_STORY_LOCAL_DIR", "ai_story/local")
    ai_story_path = Path(ai_story_local)
    if not ai_story_path.is_absolute():
        ai_story_path = project_root / ai_story_path

    chars_repo = env.get("characters_repo_local", str(project_root / "characters_repo"))
    chars_repo_path = Path(chars_repo)
    if not chars_repo_path.is_absolute():
        chars_repo_path = project_root / chars_repo

    return GlobalConfig(
        base_url=env.get("BASE_URL", env.get("game_app_service_url", "http://localhost:60002")),
        token=env.get("TOKEN", ""),
        username=env.get("user_name", "admin"),
        password=env.get("user_psw", ""),
        chub_username=env.get("CHUB_USERNAME", env.get("characters_repo_username", "")),
        chub_password=env.get("CHUB_PASSWORD", env.get("characters_repo_password", "")),
        chub_gateway=env.get("CHUB_GATEWAY", "https://gateway.chub.ai"),
        chub_ro_api=env.get("CHUB_RO_API", "https://ro.chub.ai"),
        cards_base_url=env.get("CARDS_BASE_URL", "https://cards.sillytavern.one"),
        cards_username=env.get("CARDS_USERNAME", env.get("characters_repo_username", "")),
        cards_password=env.get("CARDS_PASSWORD", env.get("characters_repo_password", "")),
        project_root=project_root,
        ai_story_local_dir=ai_story_path,
        characters_repo_dir=chars_repo_path,
        avatars_subdir=env.get("AVATARS_SUBDIR", ""),
    )


def load_story_config(story_name: str, global_cfg: GlobalConfig = None) -> StoryConfig:
    """
    加载故事配置：先读全局 .env，再读故事 .env，最后读 story.json（如有）

    story.json 放在 ai_story/local/故事名/story.json，格式:
    {
        "story_name": "破局-从冷落走到瞩目",
        "intro": "...",
        "global_bg": "...",
        "card_scenario": "...",
        "card_tags": ["Roleplay", "都市"],
        "player_role": {"name": "顾泽", "md_file": "顾泽.md", "avatar_file": "顾泽.png"},
        "npc_roles": [
            {"name": "顾子航", "md_file": "顾子航.md", "avatar_file": "顾子航.png"},
            ...
        ],
        "chapter_covers": {
            "1": {"cover": "chapter_1_cover.jpg", "background": "chapter_1_bg.jpg"},
            ...
        }
    }
    """
    if global_cfg is None:
        global_cfg = load_global_config()

    story_dir = global_cfg.ai_story_local_dir / story_name

    # 读故事 .env
    story_env = _parse_env_file(story_dir / ".env")

    # 合并配置
    story_name_resolved = story_env.get("STORY_NAME", story_name)
    world_id = int(story_env.get("WORLD_ID", "0"))
    project_id = int(story_env.get("PROJECT_ID", str(global_cfg.project_id if hasattr(global_cfg, 'project_id') else 1)))
    intro = story_env.get("STORY_INTRO", "")
    global_bg = story_env.get("STORY_GLOBAL_BG", "")

    # 角色映射：优先 story.json，降级到 .env 的 ROLE_NAME_TO_FILE/AVATAR
    story_json_path = story_dir / "story.json"
    story_json = {}
    if story_json_path.exists():
        with open(story_json_path, "r", encoding="utf-8") as f:
            story_json = json.load(f)

    # player_role
    player_role = None
    if "player_role" in story_json:
        p = story_json["player_role"]
        player_role = RoleMapping(
            name=p["name"], md_file=p["md_file"],
            avatar_file=p.get("avatar_file", ""), is_player=True
        )
    else:
        # 从 .env 推断：查找 用户.md
        name_to_file = _parse_json_env(story_env.get("ROLE_NAME_TO_FILE", {}))
        name_to_avatar = _parse_json_env(story_env.get("ROLE_NAME_TO_AVATAR", {}))
        # 检查是否有 用户.md
        user_md = story_dir / "roles" / "用户.md"
        if user_md.exists():
            # 解析 MD 获取角色名
            import re
            with open(user_md, "r", encoding="utf-8") as f:
                content = f.read()
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                try:
                    params = json.loads(json_match.group(1))
                    pname = params.get("name", "玩家")
                    player_role = RoleMapping(
                        name=pname, md_file="用户.md",
                        avatar_file=params.get("avatar_file", f"{pname}.png"),
                        is_player=True
                    )
                except json.JSONDecodeError:
                    pass

    # npc_roles
    npc_roles = []
    if "npc_roles" in story_json:
        for r in story_json["npc_roles"]:
            npc_roles.append(RoleMapping(
                name=r["name"], md_file=r["md_file"],
                avatar_file=r.get("avatar_file", "")
            ))
    else:
        name_to_file = _parse_json_env(story_env.get("ROLE_NAME_TO_FILE", {}))
        name_to_avatar = _parse_json_env(story_env.get("ROLE_NAME_TO_AVATAR", {}))
        for name, md_file in name_to_file.items():
            avatar_file = name_to_avatar.get(name, "")
            npc_roles.append(RoleMapping(
                name=name, md_file=md_file, avatar_file=avatar_file
            ))

    # 头像目录
    # story.json 中的 avatars_subdir 可覆盖全局配置（空字符串表示用根目录）
    avatars_subdir = story_json.get("avatars_subdir", global_cfg.avatars_subdir)
    avatars_dir = story_dir / "avatars"
    if avatars_subdir:
        avatars_dir = avatars_dir / avatars_subdir

    # 卡片输出目录
    cards_output_dir = global_cfg.characters_repo_dir / story_name

    # 章节封面映射
    chapter_covers = story_json.get("chapter_covers", {})

    # 卡片场景设定和标签
    card_scenario = story_json.get("card_scenario", global_bg)
    card_tags = story_json.get("card_tags", ["Roleplay"])

    return StoryConfig(
        story_name=story_name_resolved,
        story_dir=story_dir,
        world_id=world_id,
        project_id=project_id,
        intro=intro,
        global_bg=global_bg,
        player_role=player_role,
        npc_roles=npc_roles,
        roles_dir=story_dir / "roles",
        avatars_dir=avatars_dir,
        chapters_dir=story_dir / "chapters",
        image_dir=story_dir / "image",
        cards_output_dir=cards_output_dir,
        chapter_covers=chapter_covers,
        card_scenario=card_scenario,
        card_tags=card_tags,
    )


def load_config(story_name: str = None) -> tuple:
    """一键加载全局+故事配置，返回 (GlobalConfig, StoryConfig)"""
    g = load_global_config()
    if story_name is None:
        # 从全局 .env 的 CURRENT_STORY 读取
        env = _parse_env_file(g.project_root / ".env")
        story_name = env.get("CURRENT_STORY", "")
    s = load_story_config(story_name, g) if story_name else None
    return g, s
