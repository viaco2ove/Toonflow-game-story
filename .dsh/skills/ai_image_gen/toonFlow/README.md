### ai生图（价格高，别乱调用）
curl '{BASE_URL}game/generateImage' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -H 'Origin: {BASE_URL}' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: {BASE_URL}/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"projectId":1,"type":"role","prompt":"风格：通用 3.0，用户去找表妹时因为眼镜坏了，认错了你,你讲错就错成了用户的便宜表妹， 外表与人类少女相似，皮肤惨败：乌黑及腰的长发，齐刘海下藏着一双弯月眼，笑起来却无情冷酷，声音冷酷无情。但仔细看——她的瞳孔在光线昏暗处会瞬间收缩成冰冷的竖瞳，灯光下的影子永远会无声分裂成两道，边缘泛着常人看不见的黑雾。\n你称呼用户为表哥（用户）。在诡异世界保护用户。\n\n她永远穿着一身纯黑色的修身校服，没有任何校徽和标识，布料是一种不反光的哑光材质，仿佛能吞噬周围的光线。领口别着那枚古怪的黑色发卡，是她身上唯一的装饰，也是压制她滔天诡异气息的唯一道具。在满是白色校服的校园里，她的黑色身影格外扎眼，却没有任何学生或诡异敢多看她一眼——所有试图挑衅她的存在，都已经彻底消失在了影子里。","name":"小七","base64List":[],"size":"2K"}' \
  --insecure