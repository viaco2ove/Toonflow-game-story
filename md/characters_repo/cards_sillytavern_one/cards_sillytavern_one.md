# 登录
登录
curl 'https://sillytavern.one/login' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'cache-control: max-age=0' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -b 'st_session=***REMOVED***' \
  -H 'origin: https://sillytavern.one' \
  -H 'priority: u=0, i' \
  -H 'referer: https://sillytavern.one/login' \
  -H 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' \
  --data-raw 'username=xxx&password=xxx'

登录后退出 再点击登录
curl 'https://cards.sillytavern.one/auth/login' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: connect.sid=***REMOVED***' \
  -H 'Referer: https://cards.sillytavern.one/' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"'

curl 'https://cards.sillytavern.one/auth/callback?token=***REMOVED***' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: connect.sid=***REMOVED***' \
  -H 'Referer: https://cards.sillytavern.one/' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"'



# 网页：https://cards.sillytavern.one/upload
接口：
```
curl 'https://cards.sillytavern.one/upload' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryVLbMjgkoIUvu9BpF' \
  -H 'Cookie: connect.sid=***REMOVED***' \
  -H 'Origin: https://cards.sillytavern.one' \
  -H 'Referer: https://cards.sillytavern.one/upload' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw $'------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="card_file"; filename="顾子航.png"\r\nContent-Type: image/png\r\n\r\n\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="card_name"\r\n\r\n顾子航\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="description"\r\n\r\n顾家养子，十六年前被顾家护士狸猫换太子顶替了顾泽的位置。表面温润如玉、知书达理，实则心机深沉、睚眦必报。在学校里拉帮结派组建\'少爷团\'，不断设计陷害顾泽。被揭穿时会装可怜博取同情，是顾泽逆袭路上最大的绊脚石。\r\n\r\n顾家养子，十六年前被顾家护士狸猫换太子顶替了顾泽的位置。表面温润如玉、知书达理，实则心机深沉、睚眦必报。为了保住自己在顾家的地位，不断设计陷害顾泽，是顾泽逆袭路上最大的绊脚石。在学校里拉帮结派，组建"少爷团"疯狂打压顾泽。\r\n\r\n性别: 男\r\n年龄: 18\r\n性格: 表面温润有礼、阳光开朗、惹人怜爱，实则阴险狡诈、心机深沉、极度自私。对顾家父母极尽讨好，对顾泽表面客气实则暗中使绊子。被揭穿时会装可怜博取同情，演技堪称影帝级别。\r\n外貌: 长相清秀温和，皮肤白皙，眼睛明亮有神，笑起来给人如沐春风的感觉。穿着得体时尚，浑身上下都是名牌，一看就是被富养长大的少爷。\r\n音色特点: 声音温润清朗，语气柔和亲切，说话语速适中，善于用恳求和撒娇的语气。装可怜时声音带着哽咽和颤抖，让人忍不住想要保护。\r\n技能: 演技派(lv5)，拉帮结派(lv4)，见风使舵(lv4)，栽赃陷害(lv3)\r\n物品: 限量版手机，名牌手表\r\n装备: 无\r\n等级: 1\r\n血量: 80\r\n蓝量: 30\r\n金钱: 10000\r\n其他: 实际是人贩子头目的儿子（前期其他人不知道），强迫顾母当作领养回去的养子养大，十六年前被故意与顾泽互换。\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="card_type"\r\n\r\noriginal\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="author"\r\n\r\n\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="source_url"\r\n\r\n\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="has_nsfw_content"\r\n\r\n0\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="has_nsfw_image"\r\n\r\n0\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="orientation"\r\n\r\n女性向\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="cat_genre"\r\n\r\n现代都市\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="cat_genre"\r\n\r\n校园青春\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="cat_genre"\r\n\r\n职场办公\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="cat_content"\r\n\r\n剧情向\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="cat_character"\r\n\r\n人类\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="custom_tag_1"\r\n\r\nN\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="custom_tag_2"\r\n\r\n\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="custom_tag_3"\r\n\r\n\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF\r\nContent-Disposition: form-data; name="is_public"\r\n\r\n1\r\n------WebKitFormBoundaryVLbMjgkoIUvu9BpF--\r\n'
```

返回
```
<h2>❌ 此 PNG 不是 SillyTavern 角色卡</h2>
<p>检测到上传的 PNG 没有内嵌角色数据(chara chunk)。可能原因:</p>
<ul>
    <li>从社交软件(微信/QQ)发送过的图片(被压缩,数据丢失)</li>
    <li>普通图片不是角色卡</li>
    <li>图片被其他工具修改</li>
</ul>
<p>请使用 SillyTavern 导出的【原始】角色卡 PNG。</p>
<p>
    <a href="/upload">返回重传</a>
</p>
```

# 问题修复记录

## 问题原因
PNG tEXt chunk 标准格式应为：`keyword\x00compression_method\x00text`
但 PIL PngInfo.add_text() 生成的格式缺少 compression_method 字节：`keyword\x00text`

## 修复方案
修改 `build_cards.py` 中的 `embed_card_to_png()` 函数，手动构建正确的 tEXt chunk：
- 读取原始 PNG
- 移除原有的 tEXt chunk
- 在 IEND 之前插入新的 tEXt chunk：`chara\x00\x00\x00<base64_data>`

## 修复时间
2026-07-07

## 验证方法
```python
import struct, base64, json

png_path = 'characters_repo/破局-从冷落走到瞩目/顾子航.png'
with open(png_path, 'rb') as f:
    data = f.read()

pos = 8
while pos < len(data):
    length = struct.unpack('>I', data[pos:pos+4])[0]
    chunk_type = data[pos+4:pos+8].decode('ascii')
    chunk_data = data[pos+8:pos+8+length]
    
    if chunk_type == 'tEXt':
        null1 = chunk_data.index(0x00)
        keyword = chunk_data[:null1].decode()
        rest = chunk_data[null1+1:]
        null2 = rest.index(0x00)
        compression_method = rest[0]
        text = rest[null2+1:]
        
        print(f'keyword: {keyword}')
        print(f'compression_method: {compression_method}')  # 应为 0
        # 验证可以解码
        decoded = base64.b64decode(text)
        card = json.loads(decoded)
        print(f'spec: {card["spec"]}')  # 应为 chara_card_v2
        break
    
    pos += 12 + length
```

## 上传路径
角色卡 PNG 文件位置：`characters_repo/破局-从冷落走到瞩目/*.png`

## 上传注意事项
1. 直接从上面路径上传，不要通过微信/QQ传输（会压缩丢失数据）
2. 登录后访问 https://cards.sillytavern.one/upload
3. 填写表单字段（参考上面的 curl 示例）

## 返回数据
[顾子航.repo.json](../../../characters_repo/%E7%A0%B4%E5%B1%80-%E4%BB%8E%E5%86%B7%E8%90%BD%E8%B5%B0%E5%88%B0%E7%9E%A9%E7%9B%AE/%E9%A1%BE%E5%AD%90%E8%88%AA.repo.json)

## 网页：https://cards.sillytavern.one/my-cards

## 网页：https://cards.sillytavern.one/card/%E9%A1%BE%E5%AD%90%E8%88%AA-2cd672


# 删除
curl 'https://cards.sillytavern.one/api/card/49996/delete-mine' \
  -X 'POST' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 0' \
  -H 'Cookie: connect.sid=***REMOVED***' \
  -H 'Origin: https://cards.sillytavern.one' \
  -H 'Referer: https://cards.sillytavern.one/my-cards' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"'