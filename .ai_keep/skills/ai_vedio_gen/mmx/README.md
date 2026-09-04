使用 **mmx-cli**（MiniMax 官方命令行工具）进行**图生5秒视频**（基于底层的 MiniMax-H3 或 Hailuo 模型）的完整实操教程如下：

---

### 第一阶段：环境准备与登录
注意：已安装的跳过！
在终端（Terminal）或命令行工具（如 CMD/PowerShell/Git Bash）中完成以下操作：

1. **安装 mmx-cli**（需提前安装 Node.js 18 及以上版本）：
   ```bash
   npm install -g mmx-cli
   ```

2. **配置国内节点与登录**（国内用户推荐走 OAuth 登录，避免 Token 鉴权报错）：
   ```bash
   # 设置国内服务区，防止接口超时
   mmx config set --key region --value cn
   
   # 触发浏览器弹窗进行 OAuth 授权登录
   mmx auth login
   ```

---

### 第二阶段：图生 5s 视频命令

MiniMax-H3 模型支持将输入图片作为**首帧**进行视频延展，并支持自定义 4~15 秒的固定时长。

在你的图片存放目录下，打开终端，输入以下命令：

```bash
mmx video generate \
  --prompt "一个男人在阳光下缓缓抬起头，微风拂过，电影级光影，高画质" \
  --first-frame ./your_image.jpg \
  --duration 5 \
  --resolution 768P \
  --out ./output_video.mp4
```

#### 🔑 核心参数说明：
*   `--prompt "..."`：描述你希望图片中发生的具体动作和运镜（如：“镜头缓慢推进，树叶随风摇曳”）。
*   `--first-frame ./your_image.jpg`：**（关键参数）** 填入你的本地图片路径，支持 JPG/PNG/WEBP。
*   `--duration 5`：指定视频时长为 **5秒**（H3 模型支持 4-15 秒整数）。
*   `--resolution 768P`：输出分辨率（也可设为 `2K`，但生成耗时较长）。
*   `--out ./output_video.mp4`：指定视频下载保存的路径和文件名。

---

### 第三阶段：高阶玩法（首尾帧控制）

如果你有两张图（一张作为开始，一张作为结束），想用它生成这5秒的**平滑过渡动画**，可以使用首尾帧插值（SEF）模式：

```bash
mmx video generate \
  --prompt "平滑过渡，角色自然地向前走去" \
  --first-frame ./start.jpg \
  --last-frame ./end.jpg \
  --duration 5 \
  --out ./transition.mp4
```

---

### 💡 常见问题避坑：
1. **视频一直在“生成中”怎么办？**
   图生视频是异步任务，生成 5s 视频通常需要 1~3 分钟。你可以先关掉终端，稍后用任务 ID 查询进度或直接等待它后台下载完成。
2. **模型选择**：
   默认使用的是 `MiniMax-Hailuo-2.3` 模型。如果你开通了 H3 权限，想要更好的物理规律和角色一致性，可以添加参数 `--model MiniMax-H3`。
