这个工作空间是用于协助 Toonflow Game 的 ai故事设计的
可以通过workbuddy 等工具进行协助创建编辑ai故事。
# "Toonflow Game"
"Toonflow Game" 在Toonflow基础上进行的二度开发
 🚀 **多角色沉浸感ai故事游戏**: 体验沉浸式ai故事游戏，感受角色互动的魅力！

## github url
https://github.com/topics/toonflow-game
https://github.com/viaco2ove/Toonflow-game.git
https://github.com/viaco2ove/Toonflow-game-vedio-web.git
https://github.com/viaco2ove/Toonflow-game-web.git
https://github.com/viaco2ove/Toonflow-game-android.git

---
# 🌟 主要功能
多角色 ai 游戏
![img.png](img.png)

## 特殊功能
- 在输入框输入“#小游戏” 可以进行查看钓鱼等小游戏的玩法。
![img_1.png](img_1.png)

- 在输入框输入“@记忆管理 xxx” 可以要求ai 变更人物参数
如：@记忆管理 睡觉恢复，可以恢复hp mp

- 战斗属性
### 血量和蓝的恢复（hp 和mp）：" +
```
"用户住宿、睡觉和吃下恢复药物等可以恢复血量和蓝到充盈满血满蓝，" +
"要把用户参数进行修改到满血满蓝，hp 和 mp 必须直接输出数字，不能写“已恢复”“满了”“充盈”等中文状态\n" +
"### 满血：基础血量100 + 等级*10 + 特殊物品或者技能加成，如物品里的血量属性点(2)\n" +
"### 满蓝：基础蓝量100 + 等级*10 + 特殊物品或者技能加成，如物品里的蓝量属性点(2)\n" +
"### 攻击力：基础攻击力10 + 等级*10 + 特殊物品或者技能加成，如物品里的攻击点属性点(2)\n" +
"### 防御力：基础防御1 + 等级*10 + 特殊物品或者技能加成，如物品里的防御点属性点(2)\n"
```

- @记忆管理 下个章节
理论上可行
- @事件进度检测 下个事件
理论上可行

- @角色名 xxx
可以呼叫这个角色

# 当前工作空间结构
ai_story 用于放在ai 故事资料
md 用于放置规则和各种文档

# 人像取景分类（镜头构图叫法）
全身照 = 全景
七分身 = 中全景
半身照 = 中景
大头照 / 证件照 = 近景（胸像）
脸部局部 = 特写 / 大特写

## 图生图
### mmx 
如果是尽量保持原来形象。那么就是改图的意思，而不是生图
```
mmx image generate `
  --prompt "七分身，把多余的文字等去掉，正面照。保持衣服和形象。去掉多余的其他人" `
--subject-ref "type=character,image=C:/Users/viaco/.workbuddy/clipboard-images/clipboard-2026-07-01T14-44-43-179Z-a2483b97.jpg" `
  --aspect-ratio 3:4 `
--style photo `
  --n 4 `
--out-dir . `
--out-prefix "顾家大姐_test"
```
### 豆包桌面程序
直接发送图片，图像生成，输入
生成图片：七分身，把多余的文字等去掉，正面照。保持衣服和形象。去掉多余的人。


## 图生文
### mmx
然后minimax token plan 不包括视频，要用 账户钱包 里独立的api-key
大概2块8 一个视频

mmx auth login --api-key sk-api-xxxx
```
mmx video generate `
  --prompt "动起来" `
  --first-frame "C:/Users/viaco/.workbuddy/clipboard-images/clipboard-2026-07-01T14-44-43-179Z-a2483b97.jpg" `
  --download "顾家大姐_test.mp4"
```
```
mmx video generate `
  --prompt "动起来" `
  --first-frame ""D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story\ai_story\171\破局-从冷落走到瞩目\avatars\温知予.png"" `
  --download "wen_test.mp4"
```

### 豆包桌面程序
有点方便
问题是审核比较严格！！！

### 其他
- 貌似免费 veo3ai
https://www.veo3ai.io/zh/image-to-video