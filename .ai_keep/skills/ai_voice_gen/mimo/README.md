## 文本设计音色进行语音合成(mimo-v2.5-tts-voicedesign)
文本设计音色进行语音合成

curl --location --request POST 'https://api.xiaomimimo.com/v1/chat/completions' \
--header "api-key: $MIMO_API_KEY" \
--header 'Content-Type: application/json' \
--data-raw '{
    "model": "mimo-v2.5-tts-voicedesign",
    "messages": [
        {
            "role": "user",
            "content": "Give me a young male tone."
        },
        {
            "role": "assistant",
            "content": "Yes, I had a sandwich."
        }
    ],
    "audio": {
        "format": "wav",
        "optimize_text_preview": true
    }
}'

返回数据：
{
    "id": "936c1f328aae453aa6006f622fbeb1c6",
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": "",
                "role": "assistant",
                "audio": {
                    "id": "e07d62c076aa4088b35de328aa2c5ca4",
                    "data": "UklGRiS+BQBXQVZFZm10IBAAAAABAAEAwF0AAIC7AAACABAAZGF0YQC+BQD//wAA///+///////+/wAA...",
                    "expires_at": null,
                    "transcript": null
                },
                "tool_calls": null,
                "final_text_preview": "Yeah, I grabbed a sandwich earlier — it was pretty good, actually. You should try the place down the street sometime.",
                "reasoning_content": null
            }
        }
    ],
    "created": 1781070873,
    "model": "mimo-v2.5-tts-voicedesign",
    "object": "chat.completion",
    "usage": {
        "completion_tokens": 51,
        "prompt_tokens": 48,
        "total_tokens": 99,
        "completion_tokens_details": {
            "reasoning_tokens": 0
        },
        "prompt_tokens_details": {
            "cached_tokens": 3
        }
    }
}
data 可以直接播放的音频数据