# 上传章节1的api
curl '{BASE_URL}game/uploadImage' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -H 'Origin: {BASE_URL}' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: {BASE_URL}/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"projectId":1,"type":"scene","fileName":"chapter_1_background_1779947892621_fg.png","base64Data":"data:image/png;base64,iVBORw..."}' \
  --insecure