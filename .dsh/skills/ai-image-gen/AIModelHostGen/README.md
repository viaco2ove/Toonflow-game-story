# workbuddy 为例：
我当前的「生图 / 视觉生成」能力按输出类型分，核心如下：

| 能力 | 工具/入口 | 支持模式 | 说明 |
|------|-----------|----------|------|
| **文生图** | ImageGen | 文本 → 图片 | 根据文字描述直接生成图像 |
| **图生图** | ImageGen | 参考图 + 文本 → 新图 | 重绘、风格迁移、扩图、局部修改等 |
| **文生 3D 模型** | 3D模型与视频特效 skill | 文本 → 3D 模型 | 生成可旋转的 3D 资产 |
| **图生 3D 模型** | 3D模型与视频特效 skill | 图片 → 3D 模型 | 从单图重建 3D |
| **模板视频特效** | 3D模型与视频特效 skill | 图片 + 特效模板 → 动效视频 | 拥抱/变身/万物归尘等预设模板 |
| **文生视频** | VideoGen | 文本 → 视频 | 短篇视频生成 |
| **图生视频** | VideoGen | 图片 → 视频 | 静态图转动态 |

**直接回答你的问题：**
- 严格意义的「生**图**」（静态图像）：**2 种模式** —— 文生图、图生图，都走 ImageGen。
- 广义「视觉内容生成」：图片 + 3D + 视频，共 **7 种模式**。

需要我现在生成什么图？给个描述或参考图，我直接出。

# deepseek harness 
就是各种生图插件
主要原理是 调用Gemini API，openai api ，openai 协议的接口进行生图
## `dsh-image-gen` 需要两步才能在 DSH 里生效：

1. **安装 DSH 插件**（在 DSH 里执行一条命令）
2. **在 DSH Settings 里配置 API Key**（选一个 Provider：Gemini / OpenAI / DashScope / Seedream 等）

这两步完成后，`generate_image` / `edit_image` 工具就会出现在我的工具列表里，我就能直接对着你说"生成头像"来出图了。

### 安装步骤（请在你的终端执行）

```bash
# 1. 安装插件（进入 DSH 项目根目录）
cd D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story
pnpm dsh plugin --profile web add dsh-image-gen@latest
```

安装完成后：

```bash
# 2. 重启 DSH（如果需要）
```

### 配置 Provider（打开 DSH Web 界面 http://127.0.0.1:3080 → Settings → Plugins → Image generation）

| Provider | 需要什么 | 说明 |
|---------|---------|------|
| **Google Gemini** | `GEMINI_API_KEY` | 最推荐，gemini-3.1-flash-image 免费额度充足 |
| **OpenAI** | `OPENAI_API_KEY` | gpt-image-2 |
| **DashScope（通义千问）** | `DASHSCOPE_API_KEY` | qwen-image-3.0 国内速度快 |
| **Seedream（字节）** | API Key | doubao-seedream-5 |
| **本地 ComfyUI** | 填写地址 `http://127.0.0.1:8188` + 导入 Workflow JSON | 免费但需本地跑 SD 模型 |

配好之后，直接跟我说"帮我生成张晚意的头像"我就能调用 `generate_image` 工具出图了。