# convert-avatar-video-to-webp

把 `ai_vedio_gen` 生成的 mp4 角色视频头像，**完全在本地**转换为可用的
webp 动画头像 + png 背景。不走 Toonflow `/game/convertAvatarVideoToGif` HTTP 接口。

详细说明在 [SKILL.md](./SKILL.md)。

## 快速开始

```bash
python D:/Users/viaco/tools/Toonflow-game/Toonflow-game-story/.workbuddy/skills/convert-avatar-video-to-webp/convert.py \
  --mp4    "<mp4 路径>" \
  --out-dir "<输出目录>"
```

## 依赖

- ffmpeg（系统 PATH 或 `--ffmpeg`）
- Python 3.13 + onnxruntime + numpy + PIL（默认借用 birefnet venv）
- MODNet ONNX 模型（`birefnet/model-cache/modnet_photographic_portrait_matting.onnx`）
