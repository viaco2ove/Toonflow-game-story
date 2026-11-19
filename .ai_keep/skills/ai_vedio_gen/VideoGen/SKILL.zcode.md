# zcode 视频生成工具

> 查证时间：2026-11-20。结论：**ZCode 本体没有自带（内置）的视频生成工具**。
> ZCode 环境内最接近"自带"的是已安装的 **mmx 技能（MiniMax MMX CLI）**，受开关控制，见下文。

## 查证过程（为什么说没有）

1. **内置工具**：ZCode 会话内可直接调用的工具只有 文件读写、Bash、Web 搜索/抓取、
   浏览器控制（browser-use）、计算机控制（computer-use）、node_repl、图片搜索（image-search，只搜不生成）、
   文档面板（docx/pdf/pptx/xlsx 查看）等 —— 没有任何 VideoGen 类工具。
2. **官方插件**（`~/.zcode/cli/plugins/cache/zcode-plugins-official/`）：
   android-emulator / browser-use / computer-use / design / documents / image-search /
   ios-simulator / node-repl-host / pdf / plugin-creator / presentations /
   restore-legacy-sessions / skill-creator / spreadsheets / visualize / zcode-guide / zcode-site
   —— 全部插件过一遍，**无视频生成插件**。
3. **捆绑技能**（ZCode 安装目录 bundled-skills）：只有 dynamic-workflows，无视频生成。

对照：WorkBuddy 有宿主提供的 `VideoGen` 工具（见 SKILL.workbuddy.md），
minimax code 有 mcode-tools Connector 的 MiniMax Video（见 SKILL.minimaxcode.md）。
ZCode 没有等价物，**不要臆造 ZCode 工具名**。

## ZCode 环境内的可用通道：mmx 技能（条件可用）

mmx 技能装在 `~/.zcode/skills/mmx/`，底层是 MiniMax 官方 CLI（`@minimaxi/mmx`，
本机已安装于 `D:\nvm4w\nodejs\mmx`），视频走 MiniMax-Hailuo-2.3 / H3 模型。

### 启用前提（三样缺一不可）

```bash
# 1. CLI 已安装（本机已装）：npm install -g @minimaxi/mmx
# 2. 已登录（OAuth 弹窗授权）
mmx auth login
# 3. 开关打开：~/.claude/mmx.conf 里 mmx_enable=true
```

⚠️ 截至 2026-11-20 检查，`~/.claude/mmx.conf` 为 **`mmx_enable=false`**，
即 **mmx 通道当前关闭，不可用**。是否打开由用户决定，AI 不得擅自改配置开通道。

### 图生视频（立绘微动用这个）

```bash
mmx video generate \
  --prompt "角色立绘轻微呼吸起伏，发丝随风缓缓飘动，镜头完全固定不动，无运镜，人物构图不变，电影感柔光" \
  --first-frame ./角色立绘.png \
  --duration 5 \
  --resolution 768P \
  --out ./output_video.mp4
```

- `--first-frame`：本地图片作首帧（JPG/PNG/WEBP）
- `--duration`：4~15 秒整数（立绘用 5）
- `--resolution`：`768P` / `1080P` / `2K`
- 首尾帧插值加 `--last-frame ./end.jpg`

### 文生视频

```bash
mmx video generate --prompt "视频描述" --async
```

异步任务，5s 视频约 1~3 分钟出片。

## 红线（与其他通道一致）

- **不允许自己换通道、不允许自己换模型**：默认通道以
  `.workbuddy/config/ai_vedio_gen.yml` 的 `ai_vedio_gen_default_fun` 为准。
  mmx 通道只有在 `mmx_enable=true` **且** 用户明确要求时才用。
- 立绘视频要求（镜头绝对不动、9:16、720P+、5~10s、MP4）见上级
  [SKILL.md](../SKILL.md)「立绘相关视频要求」。
- 角色视频输出目录强制：`{root}/.cache/character/{story}/{rolename}/`，
  **必须显式传输出路径，不允许落默认目录**。

## 排查

| 症状 | 原因 | 解法 |
|---|---|---|
| `mmx: command not found` | CLI 未装或不在 PATH | `npm install -g @minimaxi/mmx` |
| 鉴权报错 | 未登录 / Token 模式不稳 | `mmx auth login` 走 OAuth；国内区先 `mmx config set --key region --value cn` |
| 技能不触发 | `mmx_enable=false` | 改 `~/.claude/mmx.conf` 后需用户确认 |
| 一直"生成中" | 异步任务正常耗时 | 等待 1~3 分钟，或凭任务 ID 查进度 |
| 通道选择纠结 | — | 本文件结论：ZCode 无自带工具 → 走配置文件指定的通道（当前为 openai_gen/agnes） |
