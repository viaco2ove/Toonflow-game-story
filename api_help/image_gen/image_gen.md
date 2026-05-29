# image_gen ai 生图方式
根据系统可用的工具，生图方式有以下几种：

image_gen_type: mmx/multimodal/imageGen/toonFlow

## 1. **mmx CLI**（你一直在用的）
```bash
mmx -p "图片描述" --model base
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

## 4.调用Toonfolw 的ai 生图接口
略

---

**实际选择建议：**

| 场景 | 推荐方式 |
|------|----------|
| 你已经用顺手、要批量生成 | **mmx** ✅ |
| 单张生成、想要最佳质量 | **多模态 skill** |
| 其他方式失败时的兜底 | **ImageGen** |

你现在用的 `mmx` 完全没问题，不需要换。除非你想试试多模态 skill 看看效果差异。