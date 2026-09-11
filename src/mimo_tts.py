# -*- coding: utf-8 -*-
"""调用 mimo-v2.5-tts-voicedesign 生成角色音色 wav"""
import sys, json, base64, os
import requests

APIKEY = "sk-c6vnqjo9vlht36381gcgc3le5ljyg5zruyaiolnpvthikxrl"
URL    = "https://api.xiaomimimo.com/v1/chat/completions"

FIXED_TEXT = ("恭喜，已成功复刻并合成了属于自己的声音。"
              "现在，请保持自然、清晰、稳定的语气，完整读出这段固定示例文本，"
              "用于校验音色、节奏与发音质量。"
              "愿这份新的声音陪伴你进入故事，清楚表达每一句话，"
              "也让角色在之后的对话中拥有稳定、真实、可辨识的声音表现。")

def gen_voice(voice_desc_cn: str, out_path: str) -> dict:
    payload = {
        "model": "mimo-v2.5-tts-voicedesign",
        "messages": [
            {"role": "user", "content": voice_desc_cn},
            {"role": "assistant", "content": FIXED_TEXT}
        ],
        "audio": {"format": "wav", "optimize_text_preview": True}
    }
    try:
        r = requests.post(URL, headers={"api-key": APIKEY}, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        audio_data = data["choices"][0]["message"]["audio"]["data"]
        wav_bytes = base64.b64decode(audio_data)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(wav_bytes)
        final_text = data["choices"][0]["message"].get("final_text_preview", "")
        usage = data.get("usage", {})
        return {"ok": True, "msg": "OK", "wav_path": out_path,
                "final_text": final_text, "usage": usage}
    except Exception as e:
        return {"ok": False, "msg": str(e), "wav_path": None}

if __name__ == "__main__":
    voice_desc = sys.argv[1]
    out_path   = sys.argv[2]
    result = gen_voice(voice_desc, out_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
