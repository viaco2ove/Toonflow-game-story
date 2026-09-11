---
name: ai_voice_gen
description: >-
  角色音色生成技能
---
# 角色音色生成

## 音色生成到
{root}/.cache/character/{story}/{rolename}/
下面

## 音色文件要求
15s到50s(最好40s) 的wav，小于20 MB ，24000 Hz，16bit
实例文字："恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。"
这是已经验证可用音色文件的文字内容。
## 生成方式（通道总览）
多种音色文件生成方式（生成通道）
暂时已支持
- [mimo](mimo) -小米mimo2.5 音色生成

特别注意不允许ai 自己换通道  ！！！！不允许自己换模型！！！
不允许违规。你可以发现问题，提出解决方案。但是不能自以为是！
## 配置文件
[ai_voice_gen.yml](../../config/ai_voice_gen.yml)

例子
```
ai_voice_gen_default_fun: mimo
ai_voice_mimo_url: https://api.xiaomimimo.com/v1/chat/completions
ai_voice_mimo_key: xxxx
ai_voice_mimo_model: mimo-v2.5-tts-voicedesign
```

ai_voice_gen_default_fun 代表默认使用那个通道生成
