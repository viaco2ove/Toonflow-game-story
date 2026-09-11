---
title: "ai-story-chapte-img-sync"
summary: "章节封面/背景图同步技能 - 通过 Toonflow 服务端 API 把本地封面图和背景图上传并绑定到对应章节。"
trigger:
  - 章节封面同步
  - chapter cover sync
  - 上传章节封面
  - chapterExtras
read_when:
  - 章节封面没有显示
  - backgroundPath / coverPath 为空
  - 同步故事后章节没有封面
---
# ai-story-chapte-img-sync

## 功能

把本地 `image/` 目录下的章节封面图（cover）和背景图（background）上传到 Toonflow 服务器，并通过同步故事 (`full_update.py`) 写入两个字段：

| 字段位置 | 类型 | 用途 |
|---------|------|------|
| `chapter.coverPath` / `chapter.backgroundPath` | chapter 一级字段 | 章节详情页主封面 + 主背景 |
| `world.settings.chapterExtras[].coverPath/background` | settings 嵌套字段 | 章节卡片缩略图（列表/封面流） |

服务器对这两个字段的存储行为不同（实测）：
- **chapter 的 coverPath / backgroundPath** ✅ 支持，`saveChapter` 直写
- **chapterExtras 的 coverPath / background** ✅ 支持，`saveWorld` 直写（settings 传 dict 即可，client 自动转 JSON）

## 工作流程调用
[workflow_chapter_background_img.py](/src/toonflow/workflow/workflow_chapter_background_img.py)