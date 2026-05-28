## ai 润色
目的是获取符合对应语音模式的ai 提示词
curl 'http://122.51.232.171:60002/voice/polishPrompt' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://122.51.232.171' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: http://122.51.232.171/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw $'{"text":"青年女声，约18-20岁，音色轻柔甜美如邻家妹妹，对\'表哥\'说话时带着撒娇般的黏人尾音；但语气深处藏着一丝不易察觉的冰冷和非人感，当进入战斗或面对威胁时，声音瞬间变得低沉危险，如同毒蛇吐信，温柔与残忍无缝切换","configId":27,"mode":"prompt_voice"}' \
  --insecure


## 生成音色
目的是生成符合对应语音模式的音色
curl 'http://122.51.232.171:60002/voice/generateBindingVoice' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://122.51.232.171' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: http://122.51.232.171/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"configId":27,"roleId":"npc_xiaoqi","mode":"prompt_voice","voiceId":"","referenceAudioPath":"","referenceText":"","promptText":"青年女声，轻柔甜美，黏人尾音，可切换冷感低哑声线","mixVoices":[]}' \
  --insecure
