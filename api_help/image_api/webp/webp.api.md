curl 'http://192.168.31.66:60002/game/convertAvatarVideoToGif' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer {token}' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://192.168.31.66:8088' \
  -H 'Referer: http://192.168.31.66:8088/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"projectId":1,"fileName":"先生_2026-09-04T16-41-32.mp4","base64Data":"data:video/mp4;base64,AAAAIGZ0eXBpc29t。。。"}' \
  --insecure

返回
{
    "code": 200,
    "data": {
        "taskId": 1,
        "jobId": 1,
        "status": "running",
        "progress": 1,
        "message": "开始处理视频头像",
        "errorMessage": "",
        "queuePosition": 0,
        "foregroundPath": "",
        "foregroundFilePath": "",
        "backgroundPath": "",
        "backgroundFilePath": "",
        "foregroundExt": "",
        "videoPath": "",
        "videoFilePath": "",
        "firstFramePath": "",
        "firstFrameFilePath": "",
        "durationMs": 0
    },
    "message": "成功"
}

## 进度查询

  curl ^"http://192.168.31.66:60002/game/convertAvatarVideoToGif/status^" ^
  -H ^"Accept: application/json, text/plain, */*^" ^
  -H ^"Accept-Language: zh-CN,zh;q=0.9^" ^
  -H ^"Authorization: Bearer {token}^" ^
  -H ^"Connection: keep-alive^" ^
  -H ^"Content-Type: application/json^" ^
  -H ^"Origin: http://192.168.31.66:8088^" ^
  -H ^"Referer: http://192.168.31.66:8088/^" ^
  -H ^"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36^" ^
  --data-raw ^"^{^\^"taskId^\^":1^}^" ^
  --insecure

  返回
  {
    "code": 200,
    "data": {
        "taskId": 1,
        "jobId": 1,
        "status": "running",
        "progress": 8,
        "message": "使用本地/云端抠图模型逐帧处理",
        "errorMessage": "",
        "queuePosition": 0,
        "foregroundPath": "",
        "foregroundFilePath": "",
        "backgroundPath": "",
        "backgroundFilePath": "",
        "foregroundExt": "",
        "videoPath": "",
        "videoFilePath": "",
        "firstFramePath": "",
        "firstFrameFilePath": "",
        "durationMs": 0
    },
    "message": "成功"
}

{
    "code": 200,
    "data": {
        "taskId": 1,
        "jobId": 1,
        "status": "success",
        "progress": 100,
        "message": "视频头像生成完成",
        "errorMessage": "",
        "queuePosition": 0,
        "foregroundPath": "http://127.0.0.1:60002/1/game/role/a57e6e96-e05b-4e8d-b82d-c9ac27e2844b.webp",
        "foregroundFilePath": "/1/game/role/a57e6e96-e05b-4e8d-b82d-c9ac27e2844b.webp",
        "backgroundPath": "http://127.0.0.1:60002/1/game/role/89c08372-6e99-48ad-87e7-b465893b85b0.png",
        "backgroundFilePath": "/1/game/role/89c08372-6e99-48ad-87e7-b465893b85b0.png",
        "foregroundExt": "webp",
        "videoPath": "http://127.0.0.1:60002/1/game/role/bcf75f04-ed00-4c22-8b89-f3963c362733.mp4",
        "videoFilePath": "/1/game/role/bcf75f04-ed00-4c22-8b89-f3963c362733.mp4",
        "firstFramePath": "http://127.0.0.1:60002/1/game/role/450c43e0-b22e-4d5a-afd2-3c3ef4e24b51.png",
        "firstFrameFilePath": "/1/game/role/450c43e0-b22e-4d5a-afd2-3c3ef4e24b51.png",
        "durationMs": 5042
    },
    "message": "成功"
}


## 报存故事
curl 'http://192.168.31.66:60002/game/saveWorld' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Authorization: Bearer {token}' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://192.168.31.66:8088' \
  -H 'Referer: http://192.168.31.66:8088/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"worldId":42,"projectId":1,"name":"备份 谁让这个山大王修仙的","intro":"纯小白穿越到修仙界，子承父业成了黑风寨山大王。凭借一双能看透万物财气的眼睛，他在打劫事业上混得风生水起。某日意外抢到一位重伤女仙人，从她身上获得神秘小塔，女仙人一怒之下将他丢入真正的修仙界。从此，修仙界出现了一个令人闻风丧胆的悍匪——他打劫同门、收保护费、坑人不断，却被无数底层百姓含泪跪拜为英雄。","worldGlobalBackground":"","coverPath":"/1/game/world-copy/42/9df1c0ca-bf4f-4944-aa6b-bdbe2830_20ccc7239474.jpg","publishStatus":"draft","settings":{"roles":[{"id":"npc_1","roleType":"npc","name":"红缥缈","description":"神秘的，被纯小白误抢上山的\"压寨夫人\"。\n\n身上带有神秘小塔，被主角撸下手镯后一怒之下将他丢入修仙界。\n\n是一切故事的起源。\n\n**性别**：女\n**年龄**：外表 20 岁左右，实际未知（仙人寿命长）\n**性格**：高冷、恩怨分明、易怒\n**外貌**：绝美女子，身穿白色仙裙，气质出尘，但脸色苍白（重伤状态）\n**音色特点**：清冷的女声，带有仙气\n**技能**：仙法、空间转移、重伤状态\n**物品**：神秘小塔（已被主角获得）\n**装备**：仙人服饰、破损的手镯\n**等级**：35 级\n**境界**：元婴 5 层\n**血量**：100（重伤状态）\n**蓝量**：500（仙人底蕴）\n**金钱**：0","avatarImagePrompt":"一位绝美女子，身穿白色仙裙，裙摆有破损（重伤痕迹）。脸色苍白但不掩美貌，眉头微蹙，眼神带着怒意。长发及腰，部分发丝凌乱。手腕上有破损的手镯痕迹。二次元动漫风格，半身像。","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"女声，清冷，仙气，高冷，疏离，虚弱","parameterCardJson":{"name":"红缥缈","raw_setting":"神秘的，被纯小白误抢上山的\"压寨夫人\"。身上带有神秘小塔，被主角撸下手镯后一怒之下将他丢入修仙界。是一切故事的起源。外表20岁左右，实际未知（仙人寿命长），重伤状态。","gender":"女","age":20,"level":35,"level_desc":"元婴5层","personality":"高冷、恩怨分明、易怒","appearance":"绝美女子，身穿白色仙裙，气质出尘，但脸色苍白（重伤状态）","voice":"清冷的女声，带有仙气","skills":["仙法","空间转移"],"items":["神秘小塔（已被主角获得）"],"equipment":["仙人服饰","破损的手镯"],"hp":100,"mp":500,"money":0,"other":["当前处于重伤状态"],"roleType":"npc","information":"被主角误抢上山的神秘女子，因手镯被撸走一怒之下将主角丢入修仙界，是整个故事的起源角色","role_key_information":"被主角误抢上山的神秘女子，因手镯被撸走一怒之下将主角丢入修仙界，是整个故事的起源角色","exp":0,"next_level_exp":3500},"avatarSourcePath":"/1/game/world-copy/42/dd128b80-6a87-4467-9948-42fca7fd_48d09ac48cc4.png","avatarPath":"/1/game/world-copy/42/31f60377-acb4-4bb6-a052-b4a7ecaf_f34d0db4e8af.webp","avatarBgPath":"/1/game/world-copy/42/f39433d1-5438-42ae-9a13-90bb8cb0_ecea6a93696c.png","voiceMixVoices":[],"voice":"提示词：女声，清冷，仙气，高冷，","voicePresetId":"","voiceReferenceAudioPath":"/system/voice-presets/generated/npc_1/prompt_voice_36d0539ee9eb123e.wav","voiceReferenceAudioName":"prompt_voice_36d0539ee9eb123e.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://127.0.0.1:60002/voice/audioProxy?configId=78&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F0b532f32-97e5-4254-9a12-75c654231c34.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzg4MTc2Mjk0LCJleHAiOjE4MDM3MjgyOTR9.hzuRys5ZkqTsmVXDwWErixgOrCyLaebbsEB94T4GP64","avatarVideoPath":"/1/game/world-copy/42/a637e7dc-ea03-4255-b0b0-be48ef68_313e835f3a95.mp4","avatarFirstFramePath":"/1/game/world-copy/42/41dea876-af93-49dc-afc2-ca969e97_0a8f5b712ed0.png","avatarDurationMs":5042},{"id":"npc_2","roleType":"npc","name":"李玄风","description":"稳健型修仙者，主角早期的引路人。\n\n在主角被丢入修仙界后相遇，指引他修炼之路。\n\n性格谨慎，与主角的腹黑风格形成对比。\n\n**性别**：男\n**年龄**：30 岁左右\n**性格**：稳健、谨慎、热心\n**外貌**：中年男子，穿着朴素道袍，面容和善\n**音色特点**：沉稳的中年男声\n**技能**：《青云诀》、基础仙法\n**物品**：修炼丹药若干\n**装备**：道袍、飞剑\n**等级**：15 级\n**境界**：筑基 5 层\n**血量**：300（基础 100 + 等级×10，假设筑基期=20 级）\n**蓝量**：300\n**金钱**：若干灵石","avatarImagePrompt":"一位 30 岁左右的中年男子，穿着朴素青色道袍，手持拂尘。面容和善，眼神睿智，留着短须。站姿端正，气质沉稳。二次元动漫风格，半身像。","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"男声，沉稳，温和，谨慎，儒雅，仙侠风，中年道长","parameterCardJson":{"name":"李玄风","raw_setting":"稳健型修仙者，主角早期的引路人。在主角被丢入修仙界后相遇，指引他修炼之路。性格谨慎，与主角的腹黑风格形成对比。性别：男，年龄：30岁左右，性格：稳健、谨慎、热心，外貌：中年男子，穿着朴素道袍，面容和善，音色特点：沉稳的中年男声，技能：《青云诀》、基础仙法，物品：修炼丹药若干，装备：道袍、飞剑，等级：15级，境界：筑基5层，血量：300，蓝量：300，金钱：若干灵石","gender":"男","age":30,"level":15,"level_desc":"筑基5层","personality":"稳健、谨慎、热心","appearance":"中年男子，穿着朴素道袍，面容和善","voice":"沉稳的中年男声，温和谨慎","skills":["《青云诀》","基础仙法"],"items":["修炼丹药若干"],"equipment":["道袍","飞剑"],"hp":300,"mp":300,"money":0,"other":[],"roleType":"npc","information":"主角早期的修仙引路人，性格稳健谨慎热心，境界为筑基5层","role_key_information":"主角早期的修仙引路人，性格稳健谨慎热心，境界为筑基5层","exp":0,"next_level_exp":1500},"avatarSourcePath":"/1/game/world-copy/42/ba27f127-c1e7-4d7e-b5bd-b78fad78_b9286dc2b20e.png","avatarPath":"/1/game/world-copy/42/766bf2c1-5352-41a8-a565-a0fdd880_7e8921548052.webp","avatarBgPath":"/1/game/world-copy/42/ae07b0a9-8418-4e03-b053-cbe705f7_c641ef6700fd.png","voiceMixVoices":[],"voice":"提示词：男声，沉稳，温和，谨慎，","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_e757067eb824116f_9e0e2a062f92.wav","voiceReferenceAudioName":"prompt_voice_e757067eb824116f.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2Ff3e02ca9-6a36-4f54-b68d-15fe8161a10f.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/world-copy/42/60c2aa5a-ac72-4a4f-bb03-5d0df141_3c14404c78ab.mp4","avatarFirstFramePath":"/1/game/world-copy/42/d67eff5e-6c63-483d-83ce-0976471d_0b08f7ddc870.png","avatarDurationMs":5042},{"id":"npc_3","roleType":"npc","name":"白锦儿","description":"同门师妹，被主角\"拉下水\"一起干坏事。\n\n与主角关系暧昧，是早期重要女性角色。\n\n性格天真活泼，但被主角带偏后也开始搞些小套路。\n\n**性别**：女\n**年龄**：18 岁左右\n**性格**：天真活泼、善良、容易被带偏、对主角有好感\n**外貌**：清秀少女，穿着青色宗门服饰，扎着双马尾\n**音色特点**：清脆的少女声，活泼可爱\n**技能**：基础剑法、宗门功法\n**物品**：宗门令牌、零食若干\n**装备**：青钢剑、宗门服饰\n**等级**：3 级\n**境界**：炼气 3 层\n**血量**：130\n**蓝量**：130\n**金钱**：少量灵石","avatarImagePrompt":"","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"女声,清脆,活泼,可爱,天真,明亮，温柔，魅惑","parameterCardJson":{"name":"白锦儿","raw_setting":"同门师妹，被主角拉下水一起干坏事，与主角关系暧昧，是早期重要女性角色，性格天真活泼但被主角带偏后也会搞小套路，18岁左右，清秀少女，穿青色宗门服饰扎双马尾，音色清脆少女声活泼可爱，掌握基础剑法、宗门功法，持有宗门令牌、零食若干，装备青钢剑、宗门服饰，炼气3层，等级3级，血量130，蓝量130，拥有少量灵石","gender":"女","age":18,"level":3,"level_desc":"炼气3层","personality":"天真活泼、善良、容易被带偏、对主角有好感","appearance":"清秀少女，穿着青色宗门服饰，扎着双马尾","voice":"清脆的少女声，活泼可爱","skills":["基础剑法","宗门功法"],"items":["宗门令牌","零食若干"],"equipment":["青钢剑","宗门服饰"],"hp":130,"mp":130,"money":0,"other":[],"roleType":"npc","information":"同门师妹，与主角关系暧昧，早期重要女性角色，被主角带偏后会搞小套路","role_key_information":"同门师妹，与主角关系暧昧，早期重要女性角色，被主角带偏后会搞小套路","exp":0,"next_level_exp":300},"avatarSourcePath":"/1/game/world-copy/42/7d5e697a-c7be-44c2-ad2e-129fe606_d16b95b7fd43.png","avatarPath":"/1/game/world-copy/42/37d634cb-382d-4373-a1f1-0e65ba8e_1e25c4942f26.webp","avatarBgPath":"/1/game/world-copy/42/fbb00b77-8724-4986-b1b8-15951544_5913c73bb796.png","voiceMixVoices":[],"voice":"提示词：女声,清脆,活泼,可爱,","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_88773b926f9e0dea_425401b8c469.wav","voiceReferenceAudioName":"prompt_voice_88773b926f9e0dea.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F3fef6480-bb06-45ca-812a-e7aeedbcf0d1.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/world-copy/42/c01e10b2-6f23-4143-9259-4afddd7f_e7a36cdc59aa.mp4","avatarFirstFramePath":"/1/game/world-copy/42/3c3037f7-f5e1-4e54-a296-f8b8d72e_fb7a4b25065d.png","avatarDurationMs":5042},{"id":"npc_4","roleType":"npc","name":"云火月","description":"与主角有情感线的女性角色。\n\n性格独立坚强，实力不俗。\n\n对主角的腹黑行为既无奈又欣赏。\n\n**性别**：女\n**年龄**：20 岁左右\n**性格**：独立、坚强、聪明、对主角有好感\n**外貌**：美丽女子，穿着红色或紫色服饰，长发披肩，眼神坚定\n**音色特点**：温柔的女声，带点英气\n**技能**：火系功法、剑法\n**物品**：火系法宝\n**装备**：红色服饰、宝剑\n**等级**：15 级\n**境界**：筑基 5 层\n**血量**：300\n**蓝量**：350\n**金钱**：中等灵石","avatarImagePrompt":"","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"温柔女声，英气坚定，独立清醒","parameterCardJson":{"name":"云火月","raw_setting":"与主角有情感线的女性角色。性格独立坚强，实力不俗。对主角的腹黑行为既无奈又欣赏。性别女，年龄20岁左右，性格独立、坚强、聪明、对主角有好感，外貌为美丽女子，穿着红色或紫色服饰，长发披肩，眼神坚定，音色特点为温柔的女声，带点英气，技能为火系功法、剑法，物品为火系法宝，装备为红色服饰、宝剑，等级15级，境界筑基5层，血量300，蓝量350，金钱为中等灵石","gender":"女","age":20,"level":15,"level_desc":"筑基5层","personality":"独立、坚强、聪明、对主角有好感","appearance":"美丽女子，穿着红色或紫色服饰，长发披肩，眼神坚定","voice":"温柔的女声，带点英气，音色英气坚定独立","skills":["火系功法","剑法"],"items":["火系法宝"],"equipment":["红色服饰","宝剑"],"hp":300,"mp":350,"money":0,"other":[],"roleType":"npc","information":"与主角有情感线的女性角色，性格独立坚强实力不俗，对主角的腹黑行为既无奈又欣赏","role_key_information":"与主角有情感线的女性角色，性格独立坚强实力不俗，对主角的腹黑行为既无奈又欣赏","exp":0,"next_level_exp":1500},"avatarSourcePath":"/1/game/world-copy/42/3fdec7b2-a4d5-44b1-a5dd-8c4cf012_89b7c19cd44b.png","avatarPath":"/1/game/world-copy/42/b7021ace-9d65-486e-ab26-e5c5517f_41aeae2dd464.webp","avatarBgPath":"/1/game/world-copy/42/6baabe88-deb5-4849-ba74-4278a19e_90dde52db090.png","voiceMixVoices":[],"voice":"提示词：温柔女声，英气坚定，独立","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_2c63b1269e7dae3a_4c38b0d06f80.wav","voiceReferenceAudioName":"prompt_voice_2c63b1269e7dae3a.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F8a615aa9-f893-427c-80b9-d320eb90a1e9.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/world-copy/42/e0760a60-ccf4-4932-a3f4-5b1ac1ad_1815325d1199.mp4","avatarFirstFramePath":"/1/game/world-copy/42/c81b191a-adb6-4748-be31-54abfb7e_7cf80865405e.png","avatarDurationMs":5056},{"id":"npc_5","roleType":"npc","name":"林月","description":"主角需\"除掉\"的威胁。\n\n中期对手，与主角有冲突。\n\n可能是被利用的棋子。\n\n**性别**：女\n**年龄**：20 岁左右\n**性格**：高傲、嫉妒心强、可能被利用\n**外貌**：美丽女子，穿着宗门服饰，眼神带着敌意\n**音色特点**：尖锐的女声\n**技能**：宗门功法、剑法\n**物品**：宗门令牌\n**装备**：宗门服饰、宝剑\n**等级**：15 级\n**境界**：筑基 5 层\n**血量**：300\n**蓝量**：300\n**金钱**：中等灵石","avatarImagePrompt":"","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"女声,年轻,高傲,尖锐,敌意,清冷,稍快,修仙","parameterCardJson":{"name":"林月","raw_setting":"主角需除掉的威胁，中期对手，与主角有冲突，可能是被利用的棋子","gender":"女","age":20,"level":15,"level_desc":"筑基5层","personality":"高傲、嫉妒心强、可能被利用","appearance":"美丽女子，穿着宗门服饰，眼神带着敌意","voice":"尖锐的年轻女声，音色高傲","skills":["宗门功法","剑法"],"items":["宗门令牌"],"equipment":["宗门服饰","宝剑"],"hp":300,"mp":300,"money":0,"other":[],"roleType":"npc","information":"中期与主角有冲突的对手，可能是被利用的棋子","role_key_information":"中期与主角有冲突的对手，可能是被利用的棋子","exp":0,"next_level_exp":1500},"avatarSourcePath":"/1/game/world-copy/42/e9b37854-4ef9-4b69-bdb7-d2d9e340_beb2c8622b3e.png","avatarPath":"/1/game/role/a57e6e96-e05b-4e8d-b82d-c9ac27e2844b.webp","avatarBgPath":"/1/game/role/89c08372-6e99-48ad-87e7-b465893b85b0.png","voiceMixVoices":[],"voice":"提示词：女声,年轻,高傲,尖锐,","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_40aeda30de3d13c6_7a7f76c85889.wav","voiceReferenceAudioName":"prompt_voice_40aeda30de3d13c6.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F7e9b380b-6b50-48b7-b9d5-de20ff70b3a3.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/role/bcf75f04-ed00-4c22-8b89-f3963c362733.mp4","avatarFirstFramePath":"/1/game/role/450c43e0-b22e-4d5a-afd2-3c3ef4e24b51.png","avatarDurationMs":5042},{"id":"npc_6","roleType":"npc","name":"陆青山","description":"主角出生入死的兄弟，核心盟友。\n\n宗门长老，为人正直，被主角救过命。\n\n在主角卷入栽赃陷害阴谋时，主角曾保护他。\n\n**性别**：男\n**年龄**：40 岁左右\n**性格**：正直、重情义、果断、有担当\n**外貌**：中年男子，穿着长老服饰，面容刚毅，留着短须\n**音色特点**：洪亮的中年男声，有威严\n**技能**：高阶剑法、长老权限、宗门阵法\n**物品**：长老令牌、丹药若干\n**装备**：长老服饰、宝剑\n**等级**：25 级\n**境界**：金丹 5 层\n**血量**：500\n**蓝量**：500\n**金钱**：较多灵石","avatarImagePrompt":"","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"中年男声,洪亮有威严,刚毅沉稳,语速稳健,长者气势,正气担当","parameterCardJson":{"name":"陆青山","raw_setting":"主角出生入死的兄弟，核心盟友。宗门长老，为人正直，被主角救过命。在主角卷入栽赃陷害阴谋时，主角曾保护他。","gender":"男","age":40,"level":25,"level_desc":"金丹5层","personality":"正直、重情义、果断、有担当","appearance":"中年男子，穿着长老服饰，面容刚毅，留着短须","voice":"洪亮的中年男声，有威严","skills":["高阶剑法","长老权限","宗门阵法"],"items":["长老令牌","丹药若干"],"equipment":["长老服饰","宝剑"],"hp":500,"mp":500,"money":0,"other":["拥有较多灵石"],"roleType":"npc","information":"主角出生入死的核心盟友，曾被主角救命，在主角遭遇栽赃陷害时受过主角保护，是宗门内正直有担当的金丹期长老","role_key_information":"主角出生入死的核心盟友，曾被主角救命，在主角遭遇栽赃陷害时受过主角保护，是宗门内正直有担当的金丹期长老","exp":0,"next_level_exp":2500},"avatarSourcePath":"/1/game/world-copy/42/aeabdd93-efac-4f6b-b903-c740446e_32e6ef8ed6a6.png","avatarPath":"/1/game/world-copy/42/0d60e964-a7ea-4264-9aef-53cf6d42_28ad4ad1b8d5.webp","avatarBgPath":"/1/game/world-copy/42/37509b6f-1bd6-4aac-ad6c-841f1349_2c8143e347a9.png","voiceMixVoices":[],"voice":"提示词：中年男声,洪亮有威严,刚","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_eb84e1d6f47881b1_a8191b48d590.wav","voiceReferenceAudioName":"prompt_voice_eb84e1d6f47881b1.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F107e74a5-c900-4249-b2b7-d141c40a9800.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/world-copy/42/b4f40057-ca66-46b7-96a0-f5a5a74c_e0ce007c305c.mp4","avatarFirstFramePath":"/1/game/world-copy/42/659aaf55-8550-4546-ac06-01cf3db7_cf6dbc0c6595.png","avatarDurationMs":5056},{"id":"npc_7","roleType":"npc","name":"琳琅","description":"圣地圣女，眼馋主角实力，自愿当压寨夫人。\n\n性格高冷，但被主角的\"匪道\"吸引。\n\n后期重要女性角色之一。\n\n**性别**：女\n**年龄**：20 岁左右\n**性格**：高冷、骄傲、有主见、被主角吸引\n**外貌**：绝美女子，穿着白色或银色圣女服饰，气质出尘\n**音色特点**：清冷的女声，带有圣地威严\n**技能**：圣地功法、圣女特权\n**物品**：圣女令牌、圣地宝物\n**装备**：圣女服饰、法宝\n**等级**：35 级\n**境界**：元婴 5 层\n**血量**：600\n**蓝量**：600\n**金钱**：大量灵石","avatarImagePrompt":"","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"女声，清冷高傲，圣女气质，威严疏离，语速偏慢","parameterCardJson":{"name":"琳琅","raw_setting":"圣地圣女，眼馋主角实力，自愿当压寨夫人。性格高冷，但被主角的\"匪道\"吸引。后期重要女性角色之一。性别：女，年龄：20岁左右，性格：高冷、骄傲、有主见、被主角吸引，外貌：绝美女子，穿着白色或银色圣女服饰，气质出尘，音色特点：清冷的女声，带有圣地威严，技能：圣地功法、圣女特权，物品：圣女令牌、圣地宝物，装备：圣女服饰、法宝，等级：35级，境界：元婴5层，血量：600，蓝量：600，金钱：大量灵石","gender":"女","age":20,"level":35,"level_desc":"元婴5层","personality":"高冷、骄傲、有主见、被主角吸引","appearance":"绝美女子，穿着白色或银色圣女服饰，气质出尘","voice":"清冷的女声，带有圣地威严，提示词：女声，清冷高傲，圣女气质","skills":["圣地功法","圣女特权"],"items":["圣女令牌","圣地宝物"],"equipment":["圣女服饰","法宝"],"hp":600,"mp":600,"money":0,"other":[],"roleType":"npc","information":"圣地圣女，眼馋主角实力自愿当压寨夫人，后期重要女性角色之一","role_key_information":"圣地圣女，眼馋主角实力自愿当压寨夫人，后期重要女性角色之一","exp":0,"next_level_exp":3500},"avatarSourcePath":"/1/game/world-copy/42/c7926712-6e49-42a2-bb33-03756fbb_cfcd2bf1b75e.png","avatarPath":"/1/game/world-copy/42/e93292a4-77b6-4c5d-bb25-41492fdd_cc4496e644e9.webp","avatarBgPath":"/1/game/world-copy/42/8ee09ac9-8585-4178-ba08-5b2a8c11_e9e7057c19df.png","voiceMixVoices":[],"voice":"提示词：女声，清冷高傲，圣女气质","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_0260379b535cc510_54c1eaae334c.wav","voiceReferenceAudioName":"prompt_voice_0260379b535cc510.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F89a6a505-2690-46c8-9f3e-56c3d99c9e11.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/world-copy/42/31dd9680-c993-4e47-9c38-994e440f_99988d811990.mp4","avatarFirstFramePath":"/1/game/world-copy/42/64605527-4a18-4096-83fd-baf471f7_d45f411afadc.png","avatarDurationMs":5008},{"id":"npc_8","roleType":"npc","name":"冷素心","description":"后期登场角色，疑似与魔修有关。\n\n牵出魔修线索的关键人物。\n\n性格神秘，立场不明。\n\n**性别**：女\n**年龄**：25 岁左右\n**性格**：神秘、冷静、立场不明、可能亦正亦邪\n**外貌**：美丽女子，穿着黑色或深紫色服饰，眼神深邃\n**音色特点**：低沉的女声，带有神秘感\n**技能**：魔修功法、暗杀术\n**物品**：魔修宝物\n**装备**：黑色服饰、匕首\n**等级**：35 级\n**境界**：元婴 5 层\n**血量**：550\n**蓝量**：600\n**金钱**：未知","avatarImagePrompt":"","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"女声，低沉，神秘，冷静，成熟，磁性","parameterCardJson":{"name":"冷素心","raw_setting":"后期登场角色，疑似与魔修有关，牵出魔修线索的关键人物，性格神秘，立场不明，性别女，年龄25岁左右，美丽女子，穿着黑色或深紫色服饰，眼神深邃，音色为低沉的女声带有神秘感，掌握魔修功法、暗杀术，持有魔修宝物，装备为黑色服饰、匕首，等级35级，境界元婴5层，血量550，蓝量600，金钱未知","gender":"女","age":25,"level":35,"level_desc":"元婴5层","personality":"神秘、冷静、立场不明、亦正亦邪","appearance":"美丽女子，穿着黑色或深紫色服饰，眼神深邃","voice":"低沉的女声，带有神秘感","skills":["魔修功法","暗杀术"],"items":["魔修宝物"],"equipment":["黑色服饰","匕首"],"hp":550,"mp":600,"money":0,"other":[],"roleType":"npc","information":"牵出魔修线索的关键人物，疑似与魔修有关，立场不明","role_key_information":"牵出魔修线索的关键人物，疑似与魔修有关，立场不明","exp":0,"next_level_exp":3500},"avatarSourcePath":"/1/game/world-copy/42/8310e480-5584-44ba-8f16-418b2e77_2a6741c6e2eb.png","avatarPath":"/1/game/world-copy/42/cb351e62-112d-49d0-a201-d90d76fe_2727040db711.webp","avatarBgPath":"/1/game/world-copy/42/f9d73e82-25fc-43fc-bce3-88e7814b_a74a96a8d36a.png","voiceMixVoices":[],"voice":"提示词：女声，低沉，神秘，冷静，","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_2375cdc00f4a73bf_b368e48af0f4.wav","voiceReferenceAudioName":"prompt_voice_2375cdc00f4a73bf.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2Fa82bbefd-0757-4ad5-bd0b-5f536ae6fc92.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/world-copy/42/630f9c88-6718-4a97-960f-c881695e_25f500ed9eaf.mp4","avatarFirstFramePath":"/1/game/world-copy/42/6dc6a0ee-786e-4792-a05b-1744d35e_41d308fd164b.png","avatarDurationMs":5039},{"id":"npc_9","roleType":"npc","name":"苍山道人","description":"后期登场的对手，第 260-308 章出现。\n\n与殿主失踪阴谋相关。\n\n实力强大，立场不明。\n\n**性别**：男\n**年龄**：60 岁左右\n**性格**：神秘、强大、立场不明\n**外貌**：老年男子，穿着青色道袍，面容严肃\n**音色特点**：低沉的老年男声，有威严\n**技能**：高阶功法、阵法、殿主权限\n**物品**：殿主令牌、神秘宝物\n**装备**：青色道袍、法宝\n**等级**：55 级\n**境界**：炼虚 5 层\n**血量**：1000\n**蓝量**：1000\n**金钱**：未知","avatarImagePrompt":"","attributes":{},"voiceMode":"prompt_voice","voicePromptText":"老年男声,低沉,威严,神秘,沉稳,缓慢","parameterCardJson":{"name":"苍山道人","raw_setting":"后期登场的对手，第260-308章出现。与殿主失踪阴谋相关。实力强大，立场不明。性别：男，年龄：60岁左右，性格：神秘、强大、立场不明，外貌：老年男子，穿着青色道袍，面容严肃，音色特点：低沉的老年男声，有威严，技能：高阶功法、阵法、殿主权限，物品：殿主令牌、神秘宝物，装备：青色道袍、法宝，等级：55级，境界：炼虚5层，血量：1000，蓝量：1000，金钱：未知","gender":"男","age":60,"level":55,"level_desc":"炼虚5层","personality":"神秘、强大、立场不明","appearance":"老年男子，穿着青色道袍，面容严肃","voice":"低沉的老年男声，有威严","skills":["高阶功法","阵法","殿主权限"],"items":["殿主令牌","神秘宝物"],"equipment":["青色道袍","法宝"],"hp":1000,"mp":1000,"money":0,"other":["与殿主失踪阴谋相关","实力强大立场不明","是后期登场的对手","登场于第260-308章"],"roleType":"npc","information":"后期登场的对手，关联殿主失踪阴谋，炼虚5层修为，持有殿主权限与殿主令牌","role_key_information":"后期登场的对手，关联殿主失踪阴谋，炼虚5层修为，持有殿主权限与殿主令牌","exp":0,"next_level_exp":5500},"avatarSourcePath":"/1/game/world-copy/42/1a73c021-56a2-4134-a7e8-df7cc193_3ff8260aa2e0.png","avatarPath":"/1/game/world-copy/42/d08adbde-a6df-434d-9009-43fc9694_4e23f5c72027.webp","avatarBgPath":"/1/game/world-copy/42/229f5584-bb46-49b9-85f0-01bd40ed_c30efc06a09f.png","voiceMixVoices":[],"voice":"提示词：老年男声,低沉,威严,神","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_87780e257ed794b0_1bcf2baded1b.wav","voiceReferenceAudioName":"prompt_voice_87780e257ed794b0.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F4f0cd2d6-25aa-41ad-924e-1d76e3f22cdf.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A","avatarVideoPath":"/1/game/world-copy/42/407bc8e9-4a83-4836-af7e-a7e67163_f1b9196f0dcb.mp4","avatarFirstFramePath":"/1/game/world-copy/42/ae5be74c-bc02-4db9-8aac-a5ef06af_6418d223b6c7.png","avatarDurationMs":5008},{"id":"npc_10","roleType":"general","name":"某女子","description":"某女子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的女性讲话。\n\n例如 xxx 说了什么。\n\n必须带上是饰演谁在说话。\n\n例如：（饰演欧阳娜娜）很高兴认识你。\n\n如果实在不知道在扮演谁那就：（扮演虚无）。\n\n**性别**：女\n**年龄**：不限\n**性格**：根据饰演角色变化\n**外貌**：根据饰演角色变化\n**音色特点**：标准女声（克隆）\n**等级**：1 级\n**等级称号**：初入此界","avatarImagePrompt":"","attributes":{},"voiceMode":"text","voicePromptText":"","parameterCardJson":{"name":"某女子","raw_setting":"某女子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的女性讲话。例如 xxx 说了什么。必须带上是饰演谁在说话。例如：（饰演欧阳娜娜）很高兴认识你。如果实在不知道在扮演谁那就：（扮演虚无）。性别：女，年龄：不限，性格：根据饰演角色变化，外貌：根据饰演角色变化，音色特点：标准女声（克隆），等级：1 级，等级称号：初入此界","gender":"女","age":0,"level":1,"level_desc":"初入此界","personality":"根据饰演角色变化","appearance":"根据饰演角色变化","voice":"标准女声（克隆）","skills":[],"items":[],"equipment":[],"hp":110,"mp":110,"money":0,"other":["用于扮演剧情中未明确指定身份的女性角色","发言时需标注当前饰演的具体角色名称","身份不明时标注（扮演虚无）"],"roleType":"general","information":"可扮演任意未明确设定的女性角色，发言需标注饰演对象","role_key_information":"可扮演任意未明确设定的女性角色，发言需标注饰演对象","exp":0,"next_level_exp":100},"avatarSourcePath":"/1/game/world-copy/42/bbe1672e-0524-4171-9693-23586df8_4836cbe86f70.png","avatarPath":"/1/game/world-copy/42/444ba74a-2281-4d3f-a240-1c9b93b7_0a496fbc0f28.png","avatarBgPath":"/1/game/world-copy/42/33adf662-dd2f-439b-917e-c171559b_c1ad1217b910.png","voiceMixVoices":[],"voice":"标准女声（克隆）","voicePresetId":"story_std_female","voiceReferenceAudioPath":"/1/game/world-copy/42/clone_c40a7a3d0f44a757_a0e20fbde19b.wav","voiceReferenceAudioName":"clone_c40a7a3d0f44a757.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2Fab7fd1dd-963e-47a4-8edd-dc15a2e4c925.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A"},{"id":"npc_11","roleType":"general","name":"某男子","description":"某男子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的男性讲话。\n\n例如 xxx 说了什么。\n\n必须带上是饰演谁在说话。\n\n例如：（饰演李白）很高兴认识你。\n\n如果实在不知道在扮演谁那就：（扮演虚无）。\n\n**性别**：男\n**年龄**：不限\n**性格**：根据饰演角色变化\n**外貌**：根据饰演角色变化\n**音色特点**：标准男声（克隆）\n**等级**：1 级\n**等级称号**：初入此界","avatarImagePrompt":"","attributes":{},"voiceMode":"text","voicePromptText":"","parameterCardJson":{"name":"某男子","raw_setting":"某男子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的男性讲话。例如 xxx 说了什么。必须带上是饰演谁在说话。例如：（饰演李白）很高兴认识你。如果实在不知道在扮演谁那就：（扮演虚无）。性别：男，年龄：不限，性格：根据饰演角色变化，外貌：根据饰演角色变化，音色特点：标准男声（克隆），等级：1级，等级称号：初入此界","gender":"男","age":0,"level":1,"level_desc":"初入此界","personality":"根据饰演角色变化","appearance":"根据饰演角色变化","voice":"标准男声（克隆）","skills":[],"items":[],"equipment":[],"hp":110,"mp":110,"money":0,"other":["用于扮演剧情中未明确指定的各类男性角色","发言时需标注当前饰演的具体角色身份"],"roleType":"general","information":"无固定具象设定，可灵活饰演任意未单独建档的男性角色，发言需标注饰演对象","role_key_information":"无固定具象设定，可灵活饰演任意未单独建档的男性角色，发言需标注饰演对象","exp":0,"next_level_exp":100},"avatarSourcePath":"/1/game/world-copy/42/75f24ded-3188-4789-9b76-9fd2c4f4_37821e33d722.png","avatarPath":"/1/game/world-copy/42/27c4767a-cceb-4073-8a72-a4862914_c39a868be144.png","avatarBgPath":"/1/game/world-copy/42/178391cd-87a1-4c1e-be01-e2da5767_7710e6f16b1f.png","voiceMixVoices":[],"voice":"标准男声（克隆）","voicePresetId":"story_std_male","voiceReferenceAudioPath":"/1/game/world-copy/42/clone_2b99a7fc3a0586d0_c564531db24b.wav","voiceReferenceAudioName":"clone_2b99a7fc3a0586d0.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voiceGeneratedDownloadUrl":"http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F6017b7a4-2700-4921-ac70-318ac6eec1a8.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A"}],"narratorVoice":"混合（清朗温润）","narratorVoiceMode":"text","narratorVoicePresetId":"","narratorVoiceReferenceAudioPath":"","narratorVoiceReferenceAudioName":"","narratorVoiceReferenceText":"","narratorVoicePromptText":"","narratorVoiceMixVoices":[],"intro":"纯小白穿越到修仙界，子承父业成了黑风寨山大王。凭借一双能看透万物财气的眼睛，他在打劫事业上混得风生水起。某日意外抢到一位重伤女仙人，从她身上获得神秘小塔，女仙人一怒之下将他丢入真正的修仙界。从此，修仙界出现了一个令人闻风丧胆的悍匪——他打劫同门、收保护费、坑人不断，却被无数底层百姓含泪跪拜为英雄。","globalBackground":"穿越修仙界世界观。纯小白穿越到修仙界，子承父业成为黑风寨大当家。凭借一双能看透万物财气的眼睛，以匪道行仙道，从山寨起步，最终成为修仙界传奇。\n原著为：谁让这个悍匪修仙的\n核心设定：\n- 财气眼：主角金手指，能看透万物蕴含的财气（灵气/宝物/机缘）\n- 财气等级：灰气（凡品）-> 白气（普通）-> 绿气（略有价值）-> 蓝气（中等）-> 紫气（高价值）-> 金气（极高）-> 红气（顶级机缘）\n\n修仙等级体系：\n炼气(1-10级) -> 筑基(10-20级) -> 金丹(20-30级) -> 元婴(30-40级) -> 化神(40-50级) -> 炼虚(50-60级) -> 合体(60-70级) -> 大乘(70-80级) -> 渡劫(80-90级) -> 真仙(90级以上)\n\n战斗属性：满血=100+等级×10, 满蓝=100+等级×10, 攻击=10+等级×10, 防御=1+等级×10\n\n核心主题：以匪道行仙道 - 表面悍匪打劫，实则替天行道\n世界观：非常庞大的世界地图\n地域：青岚群山、青州凡城、东周仙土、九天仙域、极域秘境、五个大陆、五大城镇\n势力：黑风寨、青云宗、六大正道宗、三魔门、散修联盟、妖族部落、天庭仙府、凡人镖局\n凡间：各种客栈，饭店，市场，官员，凡人，各种职业，各种商业@旁白 @苍山道人","coverPath":"/1/game/world-copy/42/9df1c0ca-bf4f-4944-aa6b-bdbe2830_20ccc7239474.jpg","coverBgPath":"/1/game/world-copy/42/7d6a882f-a425-42cf-a14f-ba7899d5_654810d1ba37.jpg","allowRoleView":true,"allowChatShare":true,"publishStatus":"draft","chapterExtras":[{"chapterId":77,"sort":1,"openingRole":"旁白","openingLine":"冰冷的石板硌着后背，你猛地睁开眼。脑海中涌入的信息让你意识到——你穿越了，还成了黑风寨大当家。你揉了揉眼睛，发现世界变得不一样了：周围的物品散发着不同颜色的光芒……","background":"/1/game/world-copy/42/ae4217f6-2a70-45f4-aef9-dd4ca73b_a2d5735cfa54.png","music":"","musicAutoPlay":true,"conditionVisible":false},{"chapterId":78,"sort":1,"openingRole":"旁白","openingLine":"","background":"/1/game/world-copy/42/84e845c2-30e7-4315-bc1f-e241b060_d51d94658d2b.png","music":"","musicAutoPlay":true,"conditionVisible":false}]},"playerRole":{"id":"player","roleType":"player","name":"纯小白","avatarPath":"/1/game/world-copy/42/aa38ead0-cfd6-48c0-a1d6-0c274def_6796fc46876d.webp","avatarBgPath":"/1/game/world-copy/42/93cae1cc-f612-428d-8978-7d28eec9_84feffcae99e.png","description":"穿越者，子承父业成为黑风寨大当家。\n\n拥有\"财气眼\"金手指，能看透万物蕴含的财气（灵气/宝物/机缘）。\n\n性格腹黑搞笑，以匪道行仙道，走到哪抢到哪。\n\n表面是悍匪，实则替天行道，被无数底层百姓含泪跪拜为英雄。\n\n口头禅：\"本大王\"\n\n**性别**：男\n**年龄**：20 岁左右（穿越后）\n**性格**：腹黑、搞笑、有底线、护短、不按套路出牌\n**外貌**：普通青年模样，但双眼偶尔会闪过特殊光芒（财气眼发动时）\n**音色特点**：青年男声，带点痞气，说话幽默风趣\n**技能**：财气眼、基础修炼功法\n**物品**：神秘小塔（待解锁）\n**装备**：黑风寨大当家服饰\n**等级**：1 级\n**境界**：炼气 1 层\n**血量**：110（基础 100 + 等级×10）\n**蓝量**：110（基础 100 + 等级×10）\n**金钱**：黑风寨库存","voice":"提示词：青年男声，痞气，幽默，腹","voiceMode":"prompt_voice","voicePresetId":"","voiceReferenceAudioPath":"/1/game/world-copy/42/prompt_voice_dd869b40bc5d6ebb_689400434d6c.wav","voiceReferenceAudioName":"prompt_voice_dd869b40bc5d6ebb.wav","voiceReferenceText":"恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。","voicePromptText":"青年男声，痞气，幽默，腹黑，明亮","voiceMixVoices":[],"voiceGeneratedDownloadUrl":"","sample":"","parameterCardJson":null,"avatarSourcePath":"","avatarFirstFramePath":"","avatarDurationMs":0,"avatarImagePrompt":"一位 20 岁左右的青年，穿着黑色山寨服饰，腰间挂着山寨大当家令牌。面容普通但眼神灵动，双眼隐约闪过淡金色光芒（财气眼特征）。嘴角带着痞痞的笑容，一手叉腰，一手拿着山寨大砍刀。二次元动漫风格，半身像。","avatarReferringPath":""},"narratorRole":{"id":"narrator","roleType":"narrator","name":"旁白","avatarPath":"","avatarBgPath":"","description":"负责环境推进、规则提示与节奏控制","voice":"混合（清朗温润）","voiceMode":"text","voicePresetId":"","voiceReferenceAudioPath":"","voiceReferenceAudioName":"","voiceReferenceText":"","voicePromptText":"","voiceMixVoices":[],"voiceGeneratedDownloadUrl":"","sample":"","parameterCardJson":null},"forceRefreshRoleCards":false}' \
  --insecure

  返回

  {
    "code": 200,
    "data": {
        "id": 42,
        "projectId": 1,
        "name": "备份 谁让这个山大王修仙的",
        "intro": "纯小白穿越到修仙界，子承父业成了黑风寨山大王。凭借一双能看透万物财气的眼睛，他在打劫事业上混得风生水起。某日意外抢到一位重伤女仙人，从她身上获得神秘小塔，女仙人一怒之下将他丢入真正的修仙界。从此，修仙界出现了一个令人闻风丧胆的悍匪——他打劫同门、收保护费、坑人不断，却被无数底层百姓含泪跪拜为英雄。",
        "settings": {
            "roles": [
                {
                    "id": "npc_1",
                    "roleType": "npc",
                    "name": "红缥缈",
                    "description": "神秘的，被纯小白误抢上山的\"压寨夫人\"。\n\n身上带有神秘小塔，被主角撸下手镯后一怒之下将他丢入修仙界。\n\n是一切故事的起源。\n\n**性别**：女\n**年龄**：外表 20 岁左右，实际未知（仙人寿命长）\n**性格**：高冷、恩怨分明、易怒\n**外貌**：绝美女子，身穿白色仙裙，气质出尘，但脸色苍白（重伤状态）\n**音色特点**：清冷的女声，带有仙气\n**技能**：仙法、空间转移、重伤状态\n**物品**：神秘小塔（已被主角获得）\n**装备**：仙人服饰、破损的手镯\n**等级**：35 级\n**境界**：元婴 5 层\n**血量**：100（重伤状态）\n**蓝量**：500（仙人底蕴）\n**金钱**：0",
                    "avatarImagePrompt": "一位绝美女子，身穿白色仙裙，裙摆有破损（重伤痕迹）。脸色苍白但不掩美貌，眉头微蹙，眼神带着怒意。长发及腰，部分发丝凌乱。手腕上有破损的手镯痕迹。二次元动漫风格，半身像。",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "女声，清冷，仙气，高冷，疏离，虚弱",
                    "parameterCardJson": {
                        "name": "红缥缈",
                        "raw_setting": "神秘的，被纯小白误抢上山的\"压寨夫人\"。身上带有神秘小塔，被主角撸下手镯后一怒之下将他丢入修仙界。是一切故事的起源。外表20岁左右，实际未知（仙人寿命长），重伤状态。",
                        "gender": "女",
                        "age": 20,
                        "level": 35,
                        "level_desc": "元婴5层",
                        "personality": "高冷、恩怨分明、易怒",
                        "appearance": "绝美女子，身穿白色仙裙，气质出尘，但脸色苍白（重伤状态）",
                        "voice": "清冷的女声，带有仙气",
                        "skills": [
                            "仙法",
                            "空间转移"
                        ],
                        "items": [
                            "神秘小塔（已被主角获得）"
                        ],
                        "equipment": [
                            "仙人服饰",
                            "破损的手镯"
                        ],
                        "hp": 100,
                        "mp": 500,
                        "money": 0,
                        "other": [
                            "当前处于重伤状态"
                        ],
                        "roleType": "npc",
                        "information": "被主角误抢上山的神秘女子，因手镯被撸走一怒之下将主角丢入修仙界，是整个故事的起源角色",
                        "role_key_information": "被主角误抢上山的神秘女子，因手镯被撸走一怒之下将主角丢入修仙界，是整个故事的起源角色",
                        "exp": 0,
                        "next_level_exp": 3500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/dd128b80-6a87-4467-9948-42fca7fd_48d09ac48cc4.png",
                    "avatarPath": "/1/game/world-copy/42/31f60377-acb4-4bb6-a052-b4a7ecaf_f34d0db4e8af.webp",
                    "avatarBgPath": "/1/game/world-copy/42/f39433d1-5438-42ae-9a13-90bb8cb0_ecea6a93696c.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：女声，清冷，仙气，高冷，",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/system/voice-presets/generated/npc_1/prompt_voice_36d0539ee9eb123e.wav",
                    "voiceReferenceAudioName": "prompt_voice_36d0539ee9eb123e.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://127.0.0.1:60002/voice/audioProxy?configId=78&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F0b532f32-97e5-4254-9a12-75c654231c34.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzg4MTc2Mjk0LCJleHAiOjE4MDM3MjgyOTR9.hzuRys5ZkqTsmVXDwWErixgOrCyLaebbsEB94T4GP64",
                    "avatarVideoPath": "/1/game/world-copy/42/a637e7dc-ea03-4255-b0b0-be48ef68_313e835f3a95.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/41dea876-af93-49dc-afc2-ca969e97_0a8f5b712ed0.png",
                    "avatarDurationMs": 5042
                },
                {
                    "id": "npc_2",
                    "roleType": "npc",
                    "name": "李玄风",
                    "description": "稳健型修仙者，主角早期的引路人。\n\n在主角被丢入修仙界后相遇，指引他修炼之路。\n\n性格谨慎，与主角的腹黑风格形成对比。\n\n**性别**：男\n**年龄**：30 岁左右\n**性格**：稳健、谨慎、热心\n**外貌**：中年男子，穿着朴素道袍，面容和善\n**音色特点**：沉稳的中年男声\n**技能**：《青云诀》、基础仙法\n**物品**：修炼丹药若干\n**装备**：道袍、飞剑\n**等级**：15 级\n**境界**：筑基 5 层\n**血量**：300（基础 100 + 等级×10，假设筑基期=20 级）\n**蓝量**：300\n**金钱**：若干灵石",
                    "avatarImagePrompt": "一位 30 岁左右的中年男子，穿着朴素青色道袍，手持拂尘。面容和善，眼神睿智，留着短须。站姿端正，气质沉稳。二次元动漫风格，半身像。",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "男声，沉稳，温和，谨慎，儒雅，仙侠风，中年道长",
                    "parameterCardJson": {
                        "name": "李玄风",
                        "raw_setting": "稳健型修仙者，主角早期的引路人。在主角被丢入修仙界后相遇，指引他修炼之路。性格谨慎，与主角的腹黑风格形成对比。性别：男，年龄：30岁左右，性格：稳健、谨慎、热心，外貌：中年男子，穿着朴素道袍，面容和善，音色特点：沉稳的中年男声，技能：《青云诀》、基础仙法，物品：修炼丹药若干，装备：道袍、飞剑，等级：15级，境界：筑基5层，血量：300，蓝量：300，金钱：若干灵石",
                        "gender": "男",
                        "age": 30,
                        "level": 15,
                        "level_desc": "筑基5层",
                        "personality": "稳健、谨慎、热心",
                        "appearance": "中年男子，穿着朴素道袍，面容和善",
                        "voice": "沉稳的中年男声，温和谨慎",
                        "skills": [
                            "《青云诀》",
                            "基础仙法"
                        ],
                        "items": [
                            "修炼丹药若干"
                        ],
                        "equipment": [
                            "道袍",
                            "飞剑"
                        ],
                        "hp": 300,
                        "mp": 300,
                        "money": 0,
                        "other": [],
                        "roleType": "npc",
                        "information": "主角早期的修仙引路人，性格稳健谨慎热心，境界为筑基5层",
                        "role_key_information": "主角早期的修仙引路人，性格稳健谨慎热心，境界为筑基5层",
                        "exp": 0,
                        "next_level_exp": 1500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/ba27f127-c1e7-4d7e-b5bd-b78fad78_b9286dc2b20e.png",
                    "avatarPath": "/1/game/world-copy/42/766bf2c1-5352-41a8-a565-a0fdd880_7e8921548052.webp",
                    "avatarBgPath": "/1/game/world-copy/42/ae07b0a9-8418-4e03-b053-cbe705f7_c641ef6700fd.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：男声，沉稳，温和，谨慎，",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_e757067eb824116f_9e0e2a062f92.wav",
                    "voiceReferenceAudioName": "prompt_voice_e757067eb824116f.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2Ff3e02ca9-6a36-4f54-b68d-15fe8161a10f.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/world-copy/42/60c2aa5a-ac72-4a4f-bb03-5d0df141_3c14404c78ab.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/d67eff5e-6c63-483d-83ce-0976471d_0b08f7ddc870.png",
                    "avatarDurationMs": 5042
                },
                {
                    "id": "npc_3",
                    "roleType": "npc",
                    "name": "白锦儿",
                    "description": "同门师妹，被主角\"拉下水\"一起干坏事。\n\n与主角关系暧昧，是早期重要女性角色。\n\n性格天真活泼，但被主角带偏后也开始搞些小套路。\n\n**性别**：女\n**年龄**：18 岁左右\n**性格**：天真活泼、善良、容易被带偏、对主角有好感\n**外貌**：清秀少女，穿着青色宗门服饰，扎着双马尾\n**音色特点**：清脆的少女声，活泼可爱\n**技能**：基础剑法、宗门功法\n**物品**：宗门令牌、零食若干\n**装备**：青钢剑、宗门服饰\n**等级**：3 级\n**境界**：炼气 3 层\n**血量**：130\n**蓝量**：130\n**金钱**：少量灵石",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "女声,清脆,活泼,可爱,天真,明亮，温柔，魅惑",
                    "parameterCardJson": {
                        "name": "白锦儿",
                        "raw_setting": "同门师妹，被主角拉下水一起干坏事，与主角关系暧昧，是早期重要女性角色，性格天真活泼但被主角带偏后也会搞小套路，18岁左右，清秀少女，穿青色宗门服饰扎双马尾，音色清脆少女声活泼可爱，掌握基础剑法、宗门功法，持有宗门令牌、零食若干，装备青钢剑、宗门服饰，炼气3层，等级3级，血量130，蓝量130，拥有少量灵石",
                        "gender": "女",
                        "age": 18,
                        "level": 3,
                        "level_desc": "炼气3层",
                        "personality": "天真活泼、善良、容易被带偏、对主角有好感",
                        "appearance": "清秀少女，穿着青色宗门服饰，扎着双马尾",
                        "voice": "清脆的少女声，活泼可爱",
                        "skills": [
                            "基础剑法",
                            "宗门功法"
                        ],
                        "items": [
                            "宗门令牌",
                            "零食若干"
                        ],
                        "equipment": [
                            "青钢剑",
                            "宗门服饰"
                        ],
                        "hp": 130,
                        "mp": 130,
                        "money": 0,
                        "other": [],
                        "roleType": "npc",
                        "information": "同门师妹，与主角关系暧昧，早期重要女性角色，被主角带偏后会搞小套路",
                        "role_key_information": "同门师妹，与主角关系暧昧，早期重要女性角色，被主角带偏后会搞小套路",
                        "exp": 0,
                        "next_level_exp": 300
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/7d5e697a-c7be-44c2-ad2e-129fe606_d16b95b7fd43.png",
                    "avatarPath": "/1/game/world-copy/42/37d634cb-382d-4373-a1f1-0e65ba8e_1e25c4942f26.webp",
                    "avatarBgPath": "/1/game/world-copy/42/fbb00b77-8724-4986-b1b8-15951544_5913c73bb796.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：女声,清脆,活泼,可爱,",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_88773b926f9e0dea_425401b8c469.wav",
                    "voiceReferenceAudioName": "prompt_voice_88773b926f9e0dea.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F3fef6480-bb06-45ca-812a-e7aeedbcf0d1.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/world-copy/42/c01e10b2-6f23-4143-9259-4afddd7f_e7a36cdc59aa.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/3c3037f7-f5e1-4e54-a296-f8b8d72e_fb7a4b25065d.png",
                    "avatarDurationMs": 5042
                },
                {
                    "id": "npc_4",
                    "roleType": "npc",
                    "name": "云火月",
                    "description": "与主角有情感线的女性角色。\n\n性格独立坚强，实力不俗。\n\n对主角的腹黑行为既无奈又欣赏。\n\n**性别**：女\n**年龄**：20 岁左右\n**性格**：独立、坚强、聪明、对主角有好感\n**外貌**：美丽女子，穿着红色或紫色服饰，长发披肩，眼神坚定\n**音色特点**：温柔的女声，带点英气\n**技能**：火系功法、剑法\n**物品**：火系法宝\n**装备**：红色服饰、宝剑\n**等级**：15 级\n**境界**：筑基 5 层\n**血量**：300\n**蓝量**：350\n**金钱**：中等灵石",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "温柔女声，英气坚定，独立清醒",
                    "parameterCardJson": {
                        "name": "云火月",
                        "raw_setting": "与主角有情感线的女性角色。性格独立坚强，实力不俗。对主角的腹黑行为既无奈又欣赏。性别女，年龄20岁左右，性格独立、坚强、聪明、对主角有好感，外貌为美丽女子，穿着红色或紫色服饰，长发披肩，眼神坚定，音色特点为温柔的女声，带点英气，技能为火系功法、剑法，物品为火系法宝，装备为红色服饰、宝剑，等级15级，境界筑基5层，血量300，蓝量350，金钱为中等灵石",
                        "gender": "女",
                        "age": 20,
                        "level": 15,
                        "level_desc": "筑基5层",
                        "personality": "独立、坚强、聪明、对主角有好感",
                        "appearance": "美丽女子，穿着红色或紫色服饰，长发披肩，眼神坚定",
                        "voice": "温柔的女声，带点英气，音色英气坚定独立",
                        "skills": [
                            "火系功法",
                            "剑法"
                        ],
                        "items": [
                            "火系法宝"
                        ],
                        "equipment": [
                            "红色服饰",
                            "宝剑"
                        ],
                        "hp": 300,
                        "mp": 350,
                        "money": 0,
                        "other": [],
                        "roleType": "npc",
                        "information": "与主角有情感线的女性角色，性格独立坚强实力不俗，对主角的腹黑行为既无奈又欣赏",
                        "role_key_information": "与主角有情感线的女性角色，性格独立坚强实力不俗，对主角的腹黑行为既无奈又欣赏",
                        "exp": 0,
                        "next_level_exp": 1500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/3fdec7b2-a4d5-44b1-a5dd-8c4cf012_89b7c19cd44b.png",
                    "avatarPath": "/1/game/world-copy/42/b7021ace-9d65-486e-ab26-e5c5517f_41aeae2dd464.webp",
                    "avatarBgPath": "/1/game/world-copy/42/6baabe88-deb5-4849-ba74-4278a19e_90dde52db090.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：温柔女声，英气坚定，独立",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_2c63b1269e7dae3a_4c38b0d06f80.wav",
                    "voiceReferenceAudioName": "prompt_voice_2c63b1269e7dae3a.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F8a615aa9-f893-427c-80b9-d320eb90a1e9.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/world-copy/42/e0760a60-ccf4-4932-a3f4-5b1ac1ad_1815325d1199.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/c81b191a-adb6-4748-be31-54abfb7e_7cf80865405e.png",
                    "avatarDurationMs": 5056
                },
                {
                    "id": "npc_5",
                    "roleType": "npc",
                    "name": "林月",
                    "description": "主角需\"除掉\"的威胁。\n\n中期对手，与主角有冲突。\n\n可能是被利用的棋子。\n\n**性别**：女\n**年龄**：20 岁左右\n**性格**：高傲、嫉妒心强、可能被利用\n**外貌**：美丽女子，穿着宗门服饰，眼神带着敌意\n**音色特点**：尖锐的女声\n**技能**：宗门功法、剑法\n**物品**：宗门令牌\n**装备**：宗门服饰、宝剑\n**等级**：15 级\n**境界**：筑基 5 层\n**血量**：300\n**蓝量**：300\n**金钱**：中等灵石",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "女声,年轻,高傲,尖锐,敌意,清冷,稍快,修仙",
                    "parameterCardJson": {
                        "name": "林月",
                        "raw_setting": "主角需除掉的威胁，中期对手，与主角有冲突，可能是被利用的棋子",
                        "gender": "女",
                        "age": 20,
                        "level": 15,
                        "level_desc": "筑基5层",
                        "personality": "高傲、嫉妒心强、可能被利用",
                        "appearance": "美丽女子，穿着宗门服饰，眼神带着敌意",
                        "voice": "尖锐的年轻女声，音色高傲",
                        "skills": [
                            "宗门功法",
                            "剑法"
                        ],
                        "items": [
                            "宗门令牌"
                        ],
                        "equipment": [
                            "宗门服饰",
                            "宝剑"
                        ],
                        "hp": 300,
                        "mp": 300,
                        "money": 0,
                        "other": [],
                        "roleType": "npc",
                        "information": "中期与主角有冲突的对手，可能是被利用的棋子",
                        "role_key_information": "中期与主角有冲突的对手，可能是被利用的棋子",
                        "exp": 0,
                        "next_level_exp": 1500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/e9b37854-4ef9-4b69-bdb7-d2d9e340_beb2c8622b3e.png",
                    "avatarPath": "/1/game/role/a57e6e96-e05b-4e8d-b82d-c9ac27e2844b.webp",
                    "avatarBgPath": "/1/game/role/89c08372-6e99-48ad-87e7-b465893b85b0.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：女声,年轻,高傲,尖锐,",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_40aeda30de3d13c6_7a7f76c85889.wav",
                    "voiceReferenceAudioName": "prompt_voice_40aeda30de3d13c6.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F7e9b380b-6b50-48b7-b9d5-de20ff70b3a3.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/role/bcf75f04-ed00-4c22-8b89-f3963c362733.mp4",
                    "avatarFirstFramePath": "/1/game/role/450c43e0-b22e-4d5a-afd2-3c3ef4e24b51.png",
                    "avatarDurationMs": 5042
                },
                {
                    "id": "npc_6",
                    "roleType": "npc",
                    "name": "陆青山",
                    "description": "主角出生入死的兄弟，核心盟友。\n\n宗门长老，为人正直，被主角救过命。\n\n在主角卷入栽赃陷害阴谋时，主角曾保护他。\n\n**性别**：男\n**年龄**：40 岁左右\n**性格**：正直、重情义、果断、有担当\n**外貌**：中年男子，穿着长老服饰，面容刚毅，留着短须\n**音色特点**：洪亮的中年男声，有威严\n**技能**：高阶剑法、长老权限、宗门阵法\n**物品**：长老令牌、丹药若干\n**装备**：长老服饰、宝剑\n**等级**：25 级\n**境界**：金丹 5 层\n**血量**：500\n**蓝量**：500\n**金钱**：较多灵石",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "中年男声,洪亮有威严,刚毅沉稳,语速稳健,长者气势,正气担当",
                    "parameterCardJson": {
                        "name": "陆青山",
                        "raw_setting": "主角出生入死的兄弟，核心盟友。宗门长老，为人正直，被主角救过命。在主角卷入栽赃陷害阴谋时，主角曾保护他。",
                        "gender": "男",
                        "age": 40,
                        "level": 25,
                        "level_desc": "金丹5层",
                        "personality": "正直、重情义、果断、有担当",
                        "appearance": "中年男子，穿着长老服饰，面容刚毅，留着短须",
                        "voice": "洪亮的中年男声，有威严",
                        "skills": [
                            "高阶剑法",
                            "长老权限",
                            "宗门阵法"
                        ],
                        "items": [
                            "长老令牌",
                            "丹药若干"
                        ],
                        "equipment": [
                            "长老服饰",
                            "宝剑"
                        ],
                        "hp": 500,
                        "mp": 500,
                        "money": 0,
                        "other": [
                            "拥有较多灵石"
                        ],
                        "roleType": "npc",
                        "information": "主角出生入死的核心盟友，曾被主角救命，在主角遭遇栽赃陷害时受过主角保护，是宗门内正直有担当的金丹期长老",
                        "role_key_information": "主角出生入死的核心盟友，曾被主角救命，在主角遭遇栽赃陷害时受过主角保护，是宗门内正直有担当的金丹期长老",
                        "exp": 0,
                        "next_level_exp": 2500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/aeabdd93-efac-4f6b-b903-c740446e_32e6ef8ed6a6.png",
                    "avatarPath": "/1/game/world-copy/42/0d60e964-a7ea-4264-9aef-53cf6d42_28ad4ad1b8d5.webp",
                    "avatarBgPath": "/1/game/world-copy/42/37509b6f-1bd6-4aac-ad6c-841f1349_2c8143e347a9.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：中年男声,洪亮有威严,刚",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_eb84e1d6f47881b1_a8191b48d590.wav",
                    "voiceReferenceAudioName": "prompt_voice_eb84e1d6f47881b1.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F107e74a5-c900-4249-b2b7-d141c40a9800.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/world-copy/42/b4f40057-ca66-46b7-96a0-f5a5a74c_e0ce007c305c.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/659aaf55-8550-4546-ac06-01cf3db7_cf6dbc0c6595.png",
                    "avatarDurationMs": 5056
                },
                {
                    "id": "npc_7",
                    "roleType": "npc",
                    "name": "琳琅",
                    "description": "圣地圣女，眼馋主角实力，自愿当压寨夫人。\n\n性格高冷，但被主角的\"匪道\"吸引。\n\n后期重要女性角色之一。\n\n**性别**：女\n**年龄**：20 岁左右\n**性格**：高冷、骄傲、有主见、被主角吸引\n**外貌**：绝美女子，穿着白色或银色圣女服饰，气质出尘\n**音色特点**：清冷的女声，带有圣地威严\n**技能**：圣地功法、圣女特权\n**物品**：圣女令牌、圣地宝物\n**装备**：圣女服饰、法宝\n**等级**：35 级\n**境界**：元婴 5 层\n**血量**：600\n**蓝量**：600\n**金钱**：大量灵石",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "女声，清冷高傲，圣女气质，威严疏离，语速偏慢",
                    "parameterCardJson": {
                        "name": "琳琅",
                        "raw_setting": "圣地圣女，眼馋主角实力，自愿当压寨夫人。性格高冷，但被主角的\"匪道\"吸引。后期重要女性角色之一。性别：女，年龄：20岁左右，性格：高冷、骄傲、有主见、被主角吸引，外貌：绝美女子，穿着白色或银色圣女服饰，气质出尘，音色特点：清冷的女声，带有圣地威严，技能：圣地功法、圣女特权，物品：圣女令牌、圣地宝物，装备：圣女服饰、法宝，等级：35级，境界：元婴5层，血量：600，蓝量：600，金钱：大量灵石",
                        "gender": "女",
                        "age": 20,
                        "level": 35,
                        "level_desc": "元婴5层",
                        "personality": "高冷、骄傲、有主见、被主角吸引",
                        "appearance": "绝美女子，穿着白色或银色圣女服饰，气质出尘",
                        "voice": "清冷的女声，带有圣地威严，提示词：女声，清冷高傲，圣女气质",
                        "skills": [
                            "圣地功法",
                            "圣女特权"
                        ],
                        "items": [
                            "圣女令牌",
                            "圣地宝物"
                        ],
                        "equipment": [
                            "圣女服饰",
                            "法宝"
                        ],
                        "hp": 600,
                        "mp": 600,
                        "money": 0,
                        "other": [],
                        "roleType": "npc",
                        "information": "圣地圣女，眼馋主角实力自愿当压寨夫人，后期重要女性角色之一",
                        "role_key_information": "圣地圣女，眼馋主角实力自愿当压寨夫人，后期重要女性角色之一",
                        "exp": 0,
                        "next_level_exp": 3500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/c7926712-6e49-42a2-bb33-03756fbb_cfcd2bf1b75e.png",
                    "avatarPath": "/1/game/world-copy/42/e93292a4-77b6-4c5d-bb25-41492fdd_cc4496e644e9.webp",
                    "avatarBgPath": "/1/game/world-copy/42/8ee09ac9-8585-4178-ba08-5b2a8c11_e9e7057c19df.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：女声，清冷高傲，圣女气质",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_0260379b535cc510_54c1eaae334c.wav",
                    "voiceReferenceAudioName": "prompt_voice_0260379b535cc510.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F89a6a505-2690-46c8-9f3e-56c3d99c9e11.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/world-copy/42/31dd9680-c993-4e47-9c38-994e440f_99988d811990.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/64605527-4a18-4096-83fd-baf471f7_d45f411afadc.png",
                    "avatarDurationMs": 5008
                },
                {
                    "id": "npc_8",
                    "roleType": "npc",
                    "name": "冷素心",
                    "description": "后期登场角色，疑似与魔修有关。\n\n牵出魔修线索的关键人物。\n\n性格神秘，立场不明。\n\n**性别**：女\n**年龄**：25 岁左右\n**性格**：神秘、冷静、立场不明、可能亦正亦邪\n**外貌**：美丽女子，穿着黑色或深紫色服饰，眼神深邃\n**音色特点**：低沉的女声，带有神秘感\n**技能**：魔修功法、暗杀术\n**物品**：魔修宝物\n**装备**：黑色服饰、匕首\n**等级**：35 级\n**境界**：元婴 5 层\n**血量**：550\n**蓝量**：600\n**金钱**：未知",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "女声，低沉，神秘，冷静，成熟，磁性",
                    "parameterCardJson": {
                        "name": "冷素心",
                        "raw_setting": "后期登场角色，疑似与魔修有关，牵出魔修线索的关键人物，性格神秘，立场不明，性别女，年龄25岁左右，美丽女子，穿着黑色或深紫色服饰，眼神深邃，音色为低沉的女声带有神秘感，掌握魔修功法、暗杀术，持有魔修宝物，装备为黑色服饰、匕首，等级35级，境界元婴5层，血量550，蓝量600，金钱未知",
                        "gender": "女",
                        "age": 25,
                        "level": 35,
                        "level_desc": "元婴5层",
                        "personality": "神秘、冷静、立场不明、亦正亦邪",
                        "appearance": "美丽女子，穿着黑色或深紫色服饰，眼神深邃",
                        "voice": "低沉的女声，带有神秘感",
                        "skills": [
                            "魔修功法",
                            "暗杀术"
                        ],
                        "items": [
                            "魔修宝物"
                        ],
                        "equipment": [
                            "黑色服饰",
                            "匕首"
                        ],
                        "hp": 550,
                        "mp": 600,
                        "money": 0,
                        "other": [],
                        "roleType": "npc",
                        "information": "牵出魔修线索的关键人物，疑似与魔修有关，立场不明",
                        "role_key_information": "牵出魔修线索的关键人物，疑似与魔修有关，立场不明",
                        "exp": 0,
                        "next_level_exp": 3500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/8310e480-5584-44ba-8f16-418b2e77_2a6741c6e2eb.png",
                    "avatarPath": "/1/game/world-copy/42/cb351e62-112d-49d0-a201-d90d76fe_2727040db711.webp",
                    "avatarBgPath": "/1/game/world-copy/42/f9d73e82-25fc-43fc-bce3-88e7814b_a74a96a8d36a.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：女声，低沉，神秘，冷静，",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_2375cdc00f4a73bf_b368e48af0f4.wav",
                    "voiceReferenceAudioName": "prompt_voice_2375cdc00f4a73bf.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2Fa82bbefd-0757-4ad5-bd0b-5f536ae6fc92.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/world-copy/42/630f9c88-6718-4a97-960f-c881695e_25f500ed9eaf.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/6dc6a0ee-786e-4792-a05b-1744d35e_41d308fd164b.png",
                    "avatarDurationMs": 5039
                },
                {
                    "id": "npc_9",
                    "roleType": "npc",
                    "name": "苍山道人",
                    "description": "后期登场的对手，第 260-308 章出现。\n\n与殿主失踪阴谋相关。\n\n实力强大，立场不明。\n\n**性别**：男\n**年龄**：60 岁左右\n**性格**：神秘、强大、立场不明\n**外貌**：老年男子，穿着青色道袍，面容严肃\n**音色特点**：低沉的老年男声，有威严\n**技能**：高阶功法、阵法、殿主权限\n**物品**：殿主令牌、神秘宝物\n**装备**：青色道袍、法宝\n**等级**：55 级\n**境界**：炼虚 5 层\n**血量**：1000\n**蓝量**：1000\n**金钱**：未知",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "prompt_voice",
                    "voicePromptText": "老年男声,低沉,威严,神秘,沉稳,缓慢",
                    "parameterCardJson": {
                        "name": "苍山道人",
                        "raw_setting": "后期登场的对手，第260-308章出现。与殿主失踪阴谋相关。实力强大，立场不明。性别：男，年龄：60岁左右，性格：神秘、强大、立场不明，外貌：老年男子，穿着青色道袍，面容严肃，音色特点：低沉的老年男声，有威严，技能：高阶功法、阵法、殿主权限，物品：殿主令牌、神秘宝物，装备：青色道袍、法宝，等级：55级，境界：炼虚5层，血量：1000，蓝量：1000，金钱：未知",
                        "gender": "男",
                        "age": 60,
                        "level": 55,
                        "level_desc": "炼虚5层",
                        "personality": "神秘、强大、立场不明",
                        "appearance": "老年男子，穿着青色道袍，面容严肃",
                        "voice": "低沉的老年男声，有威严",
                        "skills": [
                            "高阶功法",
                            "阵法",
                            "殿主权限"
                        ],
                        "items": [
                            "殿主令牌",
                            "神秘宝物"
                        ],
                        "equipment": [
                            "青色道袍",
                            "法宝"
                        ],
                        "hp": 1000,
                        "mp": 1000,
                        "money": 0,
                        "other": [
                            "与殿主失踪阴谋相关",
                            "实力强大立场不明",
                            "是后期登场的对手",
                            "登场于第260-308章"
                        ],
                        "roleType": "npc",
                        "information": "后期登场的对手，关联殿主失踪阴谋，炼虚5层修为，持有殿主权限与殿主令牌",
                        "role_key_information": "后期登场的对手，关联殿主失踪阴谋，炼虚5层修为，持有殿主权限与殿主令牌",
                        "exp": 0,
                        "next_level_exp": 5500
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/1a73c021-56a2-4134-a7e8-df7cc193_3ff8260aa2e0.png",
                    "avatarPath": "/1/game/world-copy/42/d08adbde-a6df-434d-9009-43fc9694_4e23f5c72027.webp",
                    "avatarBgPath": "/1/game/world-copy/42/229f5584-bb46-49b9-85f0-01bd40ed_c30efc06a09f.png",
                    "voiceMixVoices": [],
                    "voice": "提示词：老年男声,低沉,威严,神",
                    "voicePresetId": "",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_87780e257ed794b0_1bcf2baded1b.wav",
                    "voiceReferenceAudioName": "prompt_voice_87780e257ed794b0.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F4f0cd2d6-25aa-41ad-924e-1d76e3f22cdf.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A",
                    "avatarVideoPath": "/1/game/world-copy/42/407bc8e9-4a83-4836-af7e-a7e67163_f1b9196f0dcb.mp4",
                    "avatarFirstFramePath": "/1/game/world-copy/42/ae5be74c-bc02-4db9-8aac-a5ef06af_6418d223b6c7.png",
                    "avatarDurationMs": 5008
                },
                {
                    "id": "npc_10",
                    "roleType": "general",
                    "name": "某女子",
                    "description": "某女子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的女性讲话。\n\n例如 xxx 说了什么。\n\n必须带上是饰演谁在说话。\n\n例如：（饰演欧阳娜娜）很高兴认识你。\n\n如果实在不知道在扮演谁那就：（扮演虚无）。\n\n**性别**：女\n**年龄**：不限\n**性格**：根据饰演角色变化\n**外貌**：根据饰演角色变化\n**音色特点**：标准女声（克隆）\n**等级**：1 级\n**等级称号**：初入此界",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "text",
                    "voicePromptText": "",
                    "parameterCardJson": {
                        "name": "某女子",
                        "raw_setting": "某女子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的女性讲话。例如 xxx 说了什么。必须带上是饰演谁在说话。例如：（饰演欧阳娜娜）很高兴认识你。如果实在不知道在扮演谁那就：（扮演虚无）。性别：女，年龄：不限，性格：根据饰演角色变化，外貌：根据饰演角色变化，音色特点：标准女声（克隆），等级：1 级，等级称号：初入此界",
                        "gender": "女",
                        "age": 0,
                        "level": 1,
                        "level_desc": "初入此界",
                        "personality": "根据饰演角色变化",
                        "appearance": "根据饰演角色变化",
                        "voice": "标准女声（克隆）",
                        "skills": [],
                        "items": [],
                        "equipment": [],
                        "hp": 110,
                        "mp": 110,
                        "money": 0,
                        "other": [
                            "用于扮演剧情中未明确指定身份的女性角色",
                            "发言时需标注当前饰演的具体角色名称",
                            "身份不明时标注（扮演虚无）"
                        ],
                        "roleType": "general",
                        "information": "可扮演任意未明确设定的女性角色，发言需标注饰演对象",
                        "role_key_information": "可扮演任意未明确设定的女性角色，发言需标注饰演对象",
                        "exp": 0,
                        "next_level_exp": 100
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/bbe1672e-0524-4171-9693-23586df8_4836cbe86f70.png",
                    "avatarPath": "/1/game/world-copy/42/444ba74a-2281-4d3f-a240-1c9b93b7_0a496fbc0f28.png",
                    "avatarBgPath": "/1/game/world-copy/42/33adf662-dd2f-439b-917e-c171559b_c1ad1217b910.png",
                    "voiceMixVoices": [],
                    "voice": "标准女声（克隆）",
                    "voicePresetId": "story_std_female",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/clone_c40a7a3d0f44a757_a0e20fbde19b.wav",
                    "voiceReferenceAudioName": "clone_c40a7a3d0f44a757.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2Fab7fd1dd-963e-47a4-8edd-dc15a2e4c925.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A"
                },
                {
                    "id": "npc_11",
                    "roleType": "general",
                    "name": "某男子",
                    "description": "某男子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的男性讲话。\n\n例如 xxx 说了什么。\n\n必须带上是饰演谁在说话。\n\n例如：（饰演李白）很高兴认识你。\n\n如果实在不知道在扮演谁那就：（扮演虚无）。\n\n**性别**：男\n**年龄**：不限\n**性格**：根据饰演角色变化\n**外貌**：根据饰演角色变化\n**音色特点**：标准男声（克隆）\n**等级**：1 级\n**等级称号**：初入此界",
                    "avatarImagePrompt": "",
                    "attributes": {},
                    "voiceMode": "text",
                    "voicePromptText": "",
                    "parameterCardJson": {
                        "name": "某男子",
                        "raw_setting": "某男子不是一个具体的角色。用于讲述剧情和代替不是剧情内任务内的男性讲话。例如 xxx 说了什么。必须带上是饰演谁在说话。例如：（饰演李白）很高兴认识你。如果实在不知道在扮演谁那就：（扮演虚无）。性别：男，年龄：不限，性格：根据饰演角色变化，外貌：根据饰演角色变化，音色特点：标准男声（克隆），等级：1级，等级称号：初入此界",
                        "gender": "男",
                        "age": 0,
                        "level": 1,
                        "level_desc": "初入此界",
                        "personality": "根据饰演角色变化",
                        "appearance": "根据饰演角色变化",
                        "voice": "标准男声（克隆）",
                        "skills": [],
                        "items": [],
                        "equipment": [],
                        "hp": 110,
                        "mp": 110,
                        "money": 0,
                        "other": [
                            "用于扮演剧情中未明确指定的各类男性角色",
                            "发言时需标注当前饰演的具体角色身份"
                        ],
                        "roleType": "general",
                        "information": "无固定具象设定，可灵活饰演任意未单独建档的男性角色，发言需标注饰演对象",
                        "role_key_information": "无固定具象设定，可灵活饰演任意未单独建档的男性角色，发言需标注饰演对象",
                        "exp": 0,
                        "next_level_exp": 100
                    },
                    "avatarSourcePath": "/1/game/world-copy/42/75f24ded-3188-4789-9b76-9fd2c4f4_37821e33d722.png",
                    "avatarPath": "/1/game/world-copy/42/27c4767a-cceb-4073-8a72-a4862914_c39a868be144.png",
                    "avatarBgPath": "/1/game/world-copy/42/178391cd-87a1-4c1e-be01-e2da5767_7710e6f16b1f.png",
                    "voiceMixVoices": [],
                    "voice": "标准男声（克隆）",
                    "voicePresetId": "story_std_male",
                    "voiceReferenceAudioPath": "/1/game/world-copy/42/clone_2b99a7fc3a0586d0_c564531db24b.wav",
                    "voiceReferenceAudioName": "clone_2b99a7fc3a0586d0.wav",
                    "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
                    "voiceGeneratedDownloadUrl": "http://122.51.232.171/voice/audioProxy?configId=63&source=%2Fuser%2F1%2Fgame%2Fvoice-preview%2F6017b7a4-2700-4921-ac70-318ac6eec1a8.wav&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzNTA5OTUxLCJleHAiOjE3OTkwNjE5NTF9.3_uUmkUDlw_w_3VbBp0WcgQ8kFHPCWzGmjtv0y1yU8A"
                }
            ],
            "narratorVoice": "混合（清朗温润）",
            "narratorVoiceMode": "text",
            "narratorVoicePresetId": "",
            "narratorVoiceReferenceAudioPath": "",
            "narratorVoiceReferenceAudioName": "",
            "narratorVoiceReferenceText": "",
            "narratorVoicePromptText": "",
            "narratorVoiceMixVoices": [],
            "intro": "纯小白穿越到修仙界，子承父业成了黑风寨山大王。凭借一双能看透万物财气的眼睛，他在打劫事业上混得风生水起。某日意外抢到一位重伤女仙人，从她身上获得神秘小塔，女仙人一怒之下将他丢入真正的修仙界。从此，修仙界出现了一个令人闻风丧胆的悍匪——他打劫同门、收保护费、坑人不断，却被无数底层百姓含泪跪拜为英雄。",
            "globalBackground": "穿越修仙界世界观。纯小白穿越到修仙界，子承父业成为黑风寨大当家。凭借一双能看透万物财气的眼睛，以匪道行仙道，从山寨起步，最终成为修仙界传奇。\n原著为：谁让这个悍匪修仙的\n核心设定：\n- 财气眼：主角金手指，能看透万物蕴含的财气（灵气/宝物/机缘）\n- 财气等级：灰气（凡品）-> 白气（普通）-> 绿气（略有价值）-> 蓝气（中等）-> 紫气（高价值）-> 金气（极高）-> 红气（顶级机缘）\n\n修仙等级体系：\n炼气(1-10级) -> 筑基(10-20级) -> 金丹(20-30级) -> 元婴(30-40级) -> 化神(40-50级) -> 炼虚(50-60级) -> 合体(60-70级) -> 大乘(70-80级) -> 渡劫(80-90级) -> 真仙(90级以上)\n\n战斗属性：满血=100+等级×10, 满蓝=100+等级×10, 攻击=10+等级×10, 防御=1+等级×10\n\n核心主题：以匪道行仙道 - 表面悍匪打劫，实则替天行道\n世界观：非常庞大的世界地图\n地域：青岚群山、青州凡城、东周仙土、九天仙域、极域秘境、五个大陆、五大城镇\n势力：黑风寨、青云宗、六大正道宗、三魔门、散修联盟、妖族部落、天庭仙府、凡人镖局\n凡间：各种客栈，饭店，市场，官员，凡人，各种职业，各种商业@旁白 @苍山道人",
            "coverPath": "/1/game/world-copy/42/9df1c0ca-bf4f-4944-aa6b-bdbe2830_20ccc7239474.jpg",
            "coverBgPath": "/1/game/world-copy/42/7d6a882f-a425-42cf-a14f-ba7899d5_654810d1ba37.jpg",
            "allowRoleView": true,
            "allowChatShare": true,
            "publishStatus": "draft",
            "chapterExtras": [
                {
                    "chapterId": 77,
                    "sort": 1,
                    "openingRole": "旁白",
                    "openingLine": "冰冷的石板硌着后背，你猛地睁开眼。脑海中涌入的信息让你意识到——你穿越了，还成了黑风寨大当家。你揉了揉眼睛，发现世界变得不一样了：周围的物品散发着不同颜色的光芒……",
                    "background": "/1/game/world-copy/42/ae4217f6-2a70-45f4-aef9-dd4ca73b_a2d5735cfa54.png",
                    "music": "",
                    "musicAutoPlay": true,
                    "conditionVisible": false
                },
                {
                    "chapterId": 78,
                    "sort": 1,
                    "openingRole": "旁白",
                    "openingLine": "",
                    "background": "/1/game/world-copy/42/84e845c2-30e7-4315-bc1f-e241b060_d51d94658d2b.png",
                    "music": "",
                    "musicAutoPlay": true,
                    "conditionVisible": false
                }
            ]
        },
        "playerRole": {
            "id": "player",
            "name": "纯小白",
            "roleType": "player",
            "description": "穿越者，子承父业成为黑风寨大当家。\n\n拥有\"财气眼\"金手指，能看透万物蕴含的财气（灵气/宝物/机缘）。\n\n性格腹黑搞笑，以匪道行仙道，走到哪抢到哪。\n\n表面是悍匪，实则替天行道，被无数底层百姓含泪跪拜为英雄。\n\n口头禅：\"本大王\"\n\n**性别**：男\n**年龄**：20 岁左右（穿越后）\n**性格**：腹黑、搞笑、有底线、护短、不按套路出牌\n**外貌**：普通青年模样，但双眼偶尔会闪过特殊光芒（财气眼发动时）\n**音色特点**：青年男声，带点痞气，说话幽默风趣\n**技能**：财气眼、基础修炼功法\n**物品**：神秘小塔（待解锁）\n**装备**：黑风寨大当家服饰\n**等级**：1 级\n**境界**：炼气 1 层\n**血量**：110（基础 100 + 等级×10）\n**蓝量**：110（基础 100 + 等级×10）\n**金钱**：黑风寨库存",
            "avatarImagePrompt": "一位 20 岁左右的青年，穿着黑色山寨服饰，腰间挂着山寨大当家令牌。面容普通但眼神灵动，双眼隐约闪过淡金色光芒（财气眼特征）。嘴角带着痞痞的笑容，一手叉腰，一手拿着山寨大砍刀。二次元动漫风格，半身像。",
            "attributes": {},
            "avatarPath": "/1/game/world-copy/42/aa38ead0-cfd6-48c0-a1d6-0c274def_6796fc46876d.webp",
            "avatarBgPath": "/1/game/world-copy/42/93cae1cc-f612-428d-8978-7d28eec9_84feffcae99e.png",
            "voice": "提示词：青年男声，痞气，幽默，腹",
            "voiceMode": "prompt_voice",
            "voicePresetId": "",
            "voiceReferenceAudioPath": "/1/game/world-copy/42/prompt_voice_dd869b40bc5d6ebb_689400434d6c.wav",
            "voiceReferenceAudioName": "prompt_voice_dd869b40bc5d6ebb.wav",
            "voiceReferenceText": "恭喜，已成功复刻并合成了属于自己的声音。现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，用于校验音色、节奏与发音质量。愿这份新的声音陪伴你进入故事，清楚表达每一句话，也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。",
            "voicePromptText": "青年男声，痞气，幽默，腹黑，明亮",
            "voiceMixVoices": [],
            "voiceGeneratedDownloadUrl": "",
            "sample": "",
            "parameterCardJson": null,
            "avatarSourcePath": "",
            "avatarFirstFramePath": "",
            "avatarDurationMs": 0,
            "avatarReferringPath": ""
        },
        "narratorRole": {
            "id": "narrator",
            "name": "旁白",
            "roleType": "narrator",
            "description": "负责环境推进、规则提示与节奏控制",
            "attributes": {},
            "avatarPath": "",
            "avatarBgPath": "",
            "voice": "混合（清朗温润）",
            "voiceMode": "text",
            "voicePresetId": "",
            "voiceReferenceAudioPath": "",
            "voiceReferenceAudioName": "",
            "voiceReferenceText": "",
            "voicePromptText": "",
            "voiceMixVoices": [],
            "voiceGeneratedDownloadUrl": "",
            "sample": "",
            "parameterCardJson": null
        },
        "createTime": 1786862738558,
        "updateTime": 1788541267393,
        "coverPath": "/1/game/world-copy/42/9df1c0ca-bf4f-4944-aa6b-bdbe2830_20ccc7239474.jpg",
        "publishStatus": "draft",
        "coverBgPath": ""
    },
    "message": "更新世界观成功"
}