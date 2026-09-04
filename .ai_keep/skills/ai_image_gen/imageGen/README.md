## **ImageGen 生图工具**
- 需要先 `ToolSearch` 发现，再 `DeferExecuteTool` 调用
- 参数：`prompt`（图片描述）
- 也是文生图，但走的是另一条通道
- 本质是大模型调用工具查找客户端能用的工具，也就是 workbuddy,deepseek harness 等需要有这个能力
- 已验证 workbuddy 调用hy3 时能使用ImageGen 进行生图