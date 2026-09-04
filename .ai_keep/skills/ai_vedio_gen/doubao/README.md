##

## doubao-seedance-2-0-mini-260615
# 提交任务
curl -X POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的API_KEY" \
  -d '{
    "model": "doubao-seedance-2-0-mini-260615",
    "content": [
      {
        "type": "text",
        "text": "人物缓缓转头看向镜头，嘴角自然上扬微笑，头发随风轻微飘动，背景虚化，电影感柔光"
      },
      {
        "type": "image_url",
        "image_url": {
          "url": "https://你的单人照公网地址.jpg"
        }
      }
    ],
    "resolution": "720p",
    "duration": 5,
    "watermark": false
  }'

# 返回结果中的id就是任务ID，用下面的命令轮询结果
curl -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{任务ID}" \
  -H "Authorization: Bearer 你的API_KEY"