---
name: ai-story-story-sync
description: Toonflow 故事上传/同步技能。把本地故事数据（世界+角色+章节+封面）与世界书（worldbook.json）发布到服务端。触发词：上传故事、发布故事、同步世界书、上传世界书、toonflow update、worldbook import、story sync。
read_when:
  - 用户要将本地故事推送到 Toonflow 服务端
  - 需要发布/更新世界、角色、章节、封面或世界书
  - 执行 `python -m src.cli toonflow update` 或 `toonflow worldbook --op import`
---

# 故事上传同步技能 (ai-story-story-sync)

## 用途与边界

把本地故事数据**上传/同步到 Toonflow 服务端**两条线：

1. **故事主体**：世界 + 玩家角色 + NPC角色 + 章节 + 封面/背景图（一条命令五合一）
2. **世界书**：把 `worldbook/worldbook.json` 导入服务端

⚠️ 本技能只负责「推送到服务端」。本地数据 JSON 的生成见 `ai-story-data-gen` 技能；本技能假定 `story.json` / `chapters/*.json` / `worldbook/worldbook.json` 等资源已就绪。

## 前置条件

| 条件 | 说明 | 读取方 |
|------|------|--------|
| 全局 `.env` | 项目根目录，含 `BASE_URL` / `TOKEN` / 账号 | `src.config.load_global_config` |
| `story.json` | 故事目录内，世界与角色配置 | `src.config.load_config` |
| `worldbook/worldbook.json` | 世界书上传前必须存在 | `worldbook.py._load_local_worldbook` |
| `world_id` | 世界书上传强依赖，必须非空 | 见「顺序依赖」 |

## 核心命令
查看故事是否已经存在，如果存在
先调用 toonflow_agme_cache 技能（修复故事时除外），获取最新故事信息。

然后根据同步任务进行选择性操作
- 创建故事
- 同步故事
- 更新故事的部分数据：toonflow_agme_cache -》更新故事的数据到最新-》增加修改-》sync
- 修复故事：用上一次正常的 toonflow_agme_cache 数据进行修复
### 1. 上传故事（五合一）

```
python -m src.cli toonflow update --story <故事名>
```

内部流程（`src/toonflow/full_update.py`）：

1. 创建/更新世界（`story.world_id` 为空时新建，并回写 `story.json`）
2. 玩家角色（`update_player_role`）
3. NPC角色 + 头像分离（`update_npc_roles`）
4. 章节（`update_chapters`）
5. 封面/背景图（`upload_world_covers`）
6. 最终 `save_world` 落地

⚠️ **首次发布** `world_id=0` → 自动建世界并把 `world_id` 写回 `story.json`；之后保持同一世界做**增量更新**（再次 `update` 会 `get_world` 命中现有世界）。

### 2. 上传世界书

```
python -m src.cli toonflow worldbook --story <故事名> --op import [--mode replace|merge]
```

- 读取 `{story_dir}/worldbook/worldbook.json` 的 `entries`
- `--mode replace`（默认）：先删服务端旧条目再导入，等价于全量覆盖
- `--mode merge`：追加模式，不清旧

## 顺序依赖（关键）

```
update  ──(写入 world_id)──►  worldbook --op import
```

`import_worldbook` 在 `story.world_id` 为空时**直接抛 `ValueError`**。因此发布顺序固定为：**先 `update` 再 `worldbook import`**。

## 辅助命令

| 命令 | 作用 |
|------|------|
| `worldbook --op list` | 列出服务端该世界全部世界书条目 |
| `worldbook --op export` | 服务端条目导出回本地 `worldbook.json`（去掉 id/worldId/createTime/updateTime） |
| `worldbook --op save --entry '<json>'` | 新建/更新单条（entry 含 id 则更新） |
| `worldbook --op delete --entry-id <id>` | 删除单条 |
| `worldbook-build --story <故事名>` | 本地 MD → `worldbook.json`（import 前的构建步骤） |

## 典型工作流

### 首次发布（建世界 + 导世界书）

```
python -m src.cli toonflow update --story 黑塔：从超忆症开始成神
python -m src.cli toonflow worldbook --story 黑塔：从超忆症开始成神 --op import
```

### 只更新世界书（世界已存在）

```
python -m src.cli toonflow worldbook --story 黑塔：从超忆症开始成神 --op import --mode merge
```

### 改了世界书源 MD 后重新导入

```
python -m src.cli toonflow worldbook-build --story 黑塔：从超忆症开始成神
python -m src.cli toonflow worldbook --story 黑塔：从超忆症开始成神 --op import
```

### 验证服务端状态

```
python -m src.cli toonflow worldbook --story 黑塔：从超忆症开始成神 --op list
```

⚠️ **import 后必须 list 复核**：`importWorldBook` 服务端逐条吞错，即使全部失败也返回 `code=200`、`imported=0`（假成功）。**判断导入是否成功唯一标准是 `--op list` 的实际条数**，不是 import 命令的退出码或返回值。

## 发布前检查清单

- [ ] 全局 `.env` 存在且 `BASE_URL` / `TOKEN` 正确（否则 `ToonflowClient` 连接失败）
- [ ] `story.json` 字段完整（`story_name`/`world_id`/`project_id`/`intro`/`global_bg`/`player_role`/`npc_roles`/`chapter_covers`）
- [ ] `chapters/*.json` 7 字段完整且 `content==md`（见 `ai-story-data-gen`）
- [ ] `worldbook/worldbook.json` 存在且 `entries` 非空（import 前）
- [ ] `avatars/*.png`、`image/cover.png`、`image/chapter_N_bg.png` 就位
- [ ] 已确认目标环境（local `:60002` / 生产 `122.51.232.171:60002`）——看全局 `.env` 的 `BASE_URL`

## 常见错误排查

| 现象 | 根因 | 解决 |
|------|------|------|
| `story.world_id 为空，请先创建/绑定世界` | 未先跑 `update`，或世界从未创建 | 先执行 `toonflow update` |
| `本地世界书不存在: .../worldbook/worldbook.json` | 没 build 或路径错 | 先 `worldbook-build`，确认目录名 `worldbook` |
| `BASE_URL`/`TOKEN` 缺失或连接拒绝 | 全局 `.env` 未配或环境错 | 校对根目录 `.env` |
| 角色/头像上传失败 | `story.json` 的 `md_file`/`avatar_file` 与实际文件名不符 | 核对 `roles/` 与 `avatars/` 实际文件 |
| `import` 后世界书数量翻倍 | 用了 `merge` 且服务端已有旧条目 | 改用默认 `replace` 全量覆盖 |
| `import` 返回 `imported=0`、list 也为 0 | 服务端 `t_worldBook` 表缺列（如 `agentList`）或库异常 | 服务端侧修 schema/代码；本地无法绕过（2026-09-04 开发环境实测 `SQLITE_ERROR: table t_worldBook has no column named agentList`，`saveWorldBookEntry` 可暴露真错，批量 import 只假成功） |
| 头像分离失败 `overdue balance` | 服务端 AI 账户欠费（抠图走外部 AI 服务） | 服务端侧充值；角色本体已添加，可稍后单独重跑 `update` 补分离 |

## 注意事项

- `update` 命中服务器，**真实创建/修改世界**，不可随意回滚（生产环境尤甚）。
- `worldbook import` 默认 `replace` 会**清掉服务端旧世界书**再导，确认无误再跑。
- `world_id` 一旦由首次 `update` 回写进 `story.json`，后续 `update`/`import` 都绑定同一世界，不会重复建世界。
