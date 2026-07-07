# 登录
curl 'https://gateway.chub.ai/authentication/token' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'access-control-allow-credentials: True' \
  -H 'access-control-allow-origin: *' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/login' \
  -H 'samwise: ***REMOVED***' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
返回
{"status":"success","csrf_token":"***REMOVED***"}


curl 'https://gateway.chub.ai/authentication/login' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'access-control-allow-credentials: True' \
  -H 'access-control-allow-origin: *' \
  -H 'content-type: application/json' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/login' \
  -H 'samwise: ***REMOVED***' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"csrf_token":"***REMOVED***","email_or_username":"xxxx","password":"xxxx","oauth":null,"state":"","redirect_url":"https://chub.ai/login","is_mobile":"false"}'

返回
{
    "git_id": 12851522,
    "username": "xxxx",
    "samwise": "$samwise",
    "subscription": 0
}

# 网页：https://chub.ai/create_character

curl 'https://gateway.chub.ai/api/core/characters' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'ch-api-key: $samwise' \
  -H 'content-type: application/json' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/create_character' \
  -H 'samwise: $samwise' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"name":"顾子航","avatar":"https://avatars.charhub.io/avatars/uploads/images/gallery/file/fc2cf2e5-9ba1-4370-9e2f-21fc1a3d3eac/cb0cddd6-0e98-4a37-a633-2bc97bd4e741.png","description":"","tags":["Roleplay"],"is_public":true,"is_nsfw":false,"is_anonymous":false,"personality":"顾家养子，十六年前被顾家护士狸猫换太子顶替了顾泽的位置。表面温润如玉、知书达理，实则心机深沉、睚眦必报。为了保住自己在顾家的地位，不断设计陷害顾泽，是顾泽逆袭路上最大的绊脚石。在学校里拉帮结派，组建\"少爷团\"疯狂打压顾泽。\n\n性别: 男\n年龄: 18\n性格: 表面温润有礼、阳光开朗、惹人怜爱，实则阴险狡诈、心机深沉、极度自私。对顾家父母极尽讨好，对顾泽表面客气实则暗中使绊子。被揭穿时会装可怜博取同情，演技堪称影帝级别。\n外貌: 长相清秀温和，皮肤白皙，眼睛明亮有神，笑起来给人如沐春风的感觉。穿着得体时尚，浑身上下都是名牌，一看就是被富养长大的少爷。\n音色特点: 声音温润清朗，语气柔和亲切，说话语速适中，善于用恳求和撒娇的语气。装可怜时声音带着哽咽和颤抖，让人忍不住想要保护。\n技能: 演技派(lv5)，拉帮结派(lv4)，见风使舵(lv4)，栽赃陷害(lv3)\n物品: 限量版手机，名牌手表\n装备: 无\n等级: 1\n血量: 80\n蓝量: 30\n金钱: 10000\n其他: 实际是人贩子头目的儿子（前期其他人不知道），强迫顾母当作领养回去的养子养大，十六年前被故意与顾泽互换。","first_message":"让开","scenario":"","example_dialogs":"","alternate_greetings":[],"depth_prompt":{"prompt":"","depth":0},"is_unlisted":false,"extensions":{"depth_prompt":{"prompt":"","depth":0}},"character_book":null,"character_id":-1}'

上传后数据存到 [顾子航.repo.chub_ai.json](../../../characters_repo/%E7%A0%B4%E5%B1%80-%E4%BB%8E%E5%86%B7%E8%90%BD%E8%B5%B0%E5%88%B0%E7%9E%A9%E7%9B%AE/%E9%A1%BE%E5%AD%90%E8%88%AA.repo.chub_ai.json)


## 上传图片（Full image，角色的头像）
curl 'https://gateway.chub.ai/api/core/characters/{username}/gu-zi-hang-b1c8d158442d' \
  -X 'PUT' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'ch-api-key: ***REMOVED***' \
  -H 'content-type: application/json' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/edit_character/{username}/gu-zi-hang-b1c8d158442d' \
  -H 'samwise: ***REMOVED***' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"avatar":"data:image/png;base64,xxx","character_id":7353948}'

{"message":"success","success":true}

## 上传图片(search image,用于搜索)。
curl 'https://gateway.chub.ai/api/project/7353948/metadata' \
  -X 'PUT' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'ch-api-key: ***REMOVED***' \
  -H 'content-type: application/json' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/edit_character/{username}/gu-zi-hang-b1c8d158442d' \
  -H 'samwise: ***REMOVED***' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"avatar":"data:image/png;base64,xxx"}'
{"message":"success","success":true}

# https://chub.ai/my_characters

curl 'https://ro.chub.ai/search?first=50&namespace=characters&nsfw=true&nsfl=true&chub=true&count=false&topics=&exclude_mine=false&include_forks=true&sort=created_at&search=&username=xxxx&only_mine=all&my_favorites=false&min_tokens=0&page=1&bypass=true' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'ch-api-key: $samwise' \
  -H 'content-type: application/json' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/my_characters' \
  -H 'samwise: $samwise' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{}'


# https://chub.ai/characters/xxxx/gu-zi-hang-d55b6786b875

curl 'https://ro.chub.ai/api/characters/xxxx/gu-zi-hang-d55b6786b875?full=true&nocache=0.9723692798668624' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'ch-api-key: $samwise' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/characters/xxxx/gu-zi-hang-d55b6786b875' \
  -H 'samwise: $samwise' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

{"message":"success","success":true}

# https://chub.ai/edit_character/xxxx/gu-zi-hang-d55b6786b875
curl 'https://ro.chub.ai/api/characters/xxxx/gu-zi-hang-d55b6786b875?full=true&nocache=0.5691935965988969' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'ch-api-key: $samwise' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/' \
  -H 'samwise: $samwise' \
  -H 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'


curl 'https://gateway.chub.ai/api/core/characters/xxxx/gu-zi-hang-d55b6786b875' \
  -X 'PUT' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'ch-api-key: $samwise' \
  -H 'content-type: application/json' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/' \
  -H 'samwise: $samwise' \
  -H 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' \
  --data-raw '{"name":"顾子航","avatar":"https://avatars.charhub.io/avatars/xxxx/gu-zi-hang-d55b6786b875/chara_card_v2.png?width=0.5688067497732209","tagline":"","in_chat_name":"顾子航","description":"","tags":["Roleplay"],"is_public":true,"is_nsfw":false,"personality":"顾家养子，十六年前被顾家护士狸猫换太子顶替了顾泽的位置。表面温润如玉、知书达理，实则心机深沉、睚眦必报。为了保住自己在顾家的地位，不断设计陷害顾泽，是顾泽逆袭路上最大的绊脚石。在学校里拉帮结派，组建\"少爷团\"疯狂打压顾泽。\n\n性别: 男\n年龄: 18\n性格: 表面温润有礼、阳光开朗、惹人怜爱，实则阴险狡诈、心机深沉、极度自私。对顾家父母极尽讨好，对顾泽表面客气实则暗中使绊子。被揭穿时会装可怜博取同情，演技堪称影帝级别。\n外貌: 长相清秀温和，皮肤白皙，眼睛明亮有神，笑起来给人如沐春风的感觉。穿着得体时尚，浑身上下都是名牌，一看就是被富养长大的少爷。\n音色特点: 声音温润清朗，语气柔和亲切，说话语速适中，善于用恳求和撒娇的语气。装可怜时声音带着哽咽和颤抖，让人忍不住想要保护。\n技能: 演技派(lv5)，拉帮结派(lv4)，见风使舵(lv4)，栽赃陷害(lv3)\n物品: 限量版手机，名牌手表\n装备: 无\n等级: 1\n血量: 80\n蓝量: 30\n金钱: 10000\n其他: 实际是人贩子头目的儿子（前期其他人不知道），强迫顾母当作领养回去的养子养大，十六年前被故意与顾泽互换。","first_message":"让开","scenario":"","example_dialogs":"","voice_id":null,"alternate_greetings":[],"system_prompt":"","post_history_instructions":"","depth_prompt":{"depth":0,"prompt":""},"embedded_lorebook":null,"is_unlisted":false,"extensions":{"depth_prompt":{"depth":0,"prompt":""}},"character_book":null,"character_id":7353870}'



## delete
curl 'https://gateway.chub.ai/api/project/xxxx/gu-zi-hang-d55b6786b875' \
  -X 'DELETE' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'ch-api-key: $samwise' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/' \
  -H 'samwise: $samwise' \
  -H 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'


## 某个作者的角色列表
https://chub.ai/users/{username}

curl 'https://ro.chub.ai/search?first=50&namespace=characters&nsfw=true&nsfl=true&chub=true&count=false&topics=&exclude_mine=true&include_forks=true&sort=created_at&search=&username={username}&my_favorites=false&min_tokens=0&page=1&bypass=true' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'ch-api-key: $samwise' \
  -H 'content-type: application/json' \
  -H 'origin: https://chub.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://chub.ai/users/{username}' \
  -H 'samwise: $samwise' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{}'