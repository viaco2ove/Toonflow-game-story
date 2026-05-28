这个工作空间是用于协助 Toonflow Game 的 ai故事设计的

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