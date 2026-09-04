##  **mmx CLI**
```bash
mmx image "图片描述" --n 1 --aspect-ratio 16:9
```
- 直接命令行调用
- 生成的是本地文件（`image_001.jpg` 等）
- 适合批量生成、自动化脚本

## 2. **多模态内容生成 Skill**（系统优先推荐）
- 通过 `Skill` 工具调用，skill 名称：`多模态内容生成`
- 支持：文生图、文生视频、文生3D模型、图生3D模型
- 系统提示明确说"优先使用本 skill"

## 3. **ImageGen 延迟工具**
- 需要先 `ToolSearch` 发现，再 `DeferExecuteTool` 调用
- 参数：`prompt`（图片描述）
- 也是文生图，但走的是另一条通道