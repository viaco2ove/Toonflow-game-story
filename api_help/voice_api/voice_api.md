## ai 润色
目的是获取符合对应语音模式的ai 提示词
curl '{BASE_URL}voice/polishPrompt' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -H 'Origin: {BASE_URL}' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: {BASE_URL}/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw $'{"text":"青年女声，约18-20岁，音色轻柔甜美如邻家妹妹，对\'表哥\'说话时带着撒娇般的黏人尾音；但语气深处藏着一丝不易察觉的冰冷和非人感，当进入战斗或面对威胁时，声音瞬间变得低沉危险，如同毒蛇吐信，温柔与残忍无缝切换","configId":27,"mode":"prompt_voice"}' \
  --insecure


## 生成音色
目的是生成符合对应语音模式的音色
curl '{BASE_URL}voice/generateBindingVoice' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -H 'Origin: {BASE_URL}' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: {BASE_URL}/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"configId":27,"roleId":"npc_xiaoqi","mode":"prompt_voice","voiceId":"","referenceAudioPath":"","referenceText":"","promptText":"青年女声，轻柔甜美，黏人尾音，可切换冷感低哑声线","mixVoices":[]}' \
  --insecure

## 试听音色
curl '{BASE_URL}voice/preview' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -H 'Origin: {BASE_URL}' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: {BASE_URL}/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"configId":27,"roleId":"npc_xiaoqi","text":"恭喜，已成功复刻或生成了属于角色的声音！","mode":"clone","voiceId":"qwen-tts-vd-story_pro_ffbcf6-voice-20260528144616492-c24b","referenceAudioPath":"/system/voice-presets/generated/npc_xiaoqi/prompt_voice_a4bc0937e5e5aa65.wav","referenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","promptText":"","mixVoices":[]}' \
  --insecure