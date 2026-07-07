# 角色卡仓库
cards.sillytavern.one
chub.ai/characters
discord.gg/hcQxUWgDVq

# 角色卡格式
两者**格式完全一致**，互相兼容。本质上用的是同一套规范：

---

## 核心结论

| 对比项 | Chub.ai | sillytavern.one |
|--------|---------|-----------------|
| **文件格式** | PNG（嵌入JSON） | PNG（嵌入JSON） |
| **嵌入方式** | PNG tEXt chunk | PNG tEXt chunk |
| **V2 chunk名** | `chara` | `chara` |
| **V3 chunk名** | `ccv3` | `ccv3` |
| **编码方式** | Base64(UTF-8 JSON) | Base64(UTF-8 JSON) |
| **V2规范** | `spec: "chara_card_v2"` | `spec: "chara_card_v2"` |
| **V3规范** | `spec: "chara_card_v3"` | `spec: "chara_card_v3"` |
| **JSON纯文本** | 同时支持 | 同时支持 |
| **互导兼容** | ✅ 可直接导入对方 | ✅ 可直接导入对方 |

**两个网站的角色卡可以互相导入，不需要任何转换。**

---

## 为什么一致

因为它们都遵循同一个开放规范：
- **V2**：`github.com/malfoyslastname/character-card-spec-v2`
- **V3**：`github.com/kwaroran/character-card-spec-v3`

这套规范是 SillyTavern 社区制定的开放标准，任何角色卡网站只要想兼容 SillyTavern（这是必须的），就必须按这个格式来。所以 Chub.ai、sillytavern.one、CharacterHub 等所有站点的卡，底层格式完全相同。

---

## 唯一的区别

不在格式，而在**内容来源和语言**：

| | Chub.ai | sillytavern.one |
|--|---------|-----------------|
| 卡片数量 | 百万级 | 35000+ |
| 语言 | 英文为主（~95%） | 中文为主（~30%中文+70%英文翻译） |
| 内容来源 | 全球作者上传 | 自动抓取+人工筛选+中文翻译 |
| 访问 | 需要梯子 | 国内直连 |

---

## 实际操作

1. **从 Chub.ai 下载的 PNG** → 直接拖进 sillytavern.one 的 SillyTavern Pro 或本地 SillyTavern → 正常使用
2. **从 sillytavern.one 下载的 PNG** → 直接导入 Chub.ai 或本地 SillyTavern → 正常使用
3. **唯一的坑**：下载时一定要用「Download」按钮直接保存，不要右键另存预览图——否则 PNG 的 tEXt chunk 可能在 CDN 优化中被丢掉，导致卡变成纯图片

# ai 故事与角色卡
首先是各种角色可以转化为角色卡
然后是故事本身就算角色卡+世界书。

