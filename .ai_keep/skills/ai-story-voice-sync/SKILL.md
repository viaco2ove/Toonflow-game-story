---
name: ai-story-voice-sync
description: Toonflow 故事 的角色音色文件上传
read_when:
  - 用户要将本地色音色文件推送到 Toonflow 服务端 的一个故事里
---
"""
python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op getWorld {worldId}

python -m src.cli toonflow client --op uploadAudio --entry /path/to/voice.wav --project-id 1
保存故事
python -m src.cli toonflow worldbook --story 谁让这个山大王修仙的 --op save_update xxx

"""

## 色音色文件上传的工作流程调用
[workflow_voice_file_up_save.py](/src/toonflow/workflow/workflow_voice_file_up_save.py)

