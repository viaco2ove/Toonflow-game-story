#!/usr/bin/env python3
"""
批量生成角色音色并更新世界设置（修复版）
使用 /voice/generateBindingVoice 接口为每个角色生成音色文件
"""

import urllib.request
import json
import time

BASE_URL = 'http://122.51.232.171:60002'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6ImFkbWluIiwiaWF0IjoxNzc5OTEwMDA5LCJleHAiOjE3OTU0NjIwMDl9.FlDWRs9KmFo97rt9sob8emsQC5IXdVUZTlvC6wXCNL8'
WORLD_ID = 35

def api_call(path, data):
    """发送API请求"""
    url = f'{BASE_URL}{path}'
    req = urllib.request.Request(
        url,
        data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {TOKEN}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'code': 500, 'message': str(e)}

def get_world_settings():
    """获取世界设置"""
    result = api_call('/game/getWorld', {'worldId': WORLD_ID})
    if result.get('code') == 200:
        return result.get('data', {})
    return None

def get_roles():
    """获取所有角色"""
    world_data = get_world_settings()
    if world_data:
        settings = world_data.get('settings', '{}')
        if isinstance(settings, str):
            settings = json.loads(settings)
        return settings.get('roles', [])
    return []

def generate_voice_for_role(role):
    """为单个角色生成音色"""
    role_id = role.get('id', '')
    role_name = role.get('name', '')
    voice_mode = role.get('voiceMode', 'prompt_voice')
    prompt_text = role.get('voicePromptText', '')

    # 清理promptText（去掉"提示词："前缀如果有的话）
    if prompt_text.startswith('提示词：'):
        prompt_text = prompt_text[4:]

    print(f"\n正在生成【{role_name}】({role_id})的音色...")
    print(f"  模式: {voice_mode}")
    print(f"  提示词: {prompt_text[:80]}..." if len(prompt_text) > 80 else f"  提示词: {prompt_text}")

    # 调用音色生成API
    payload = {
        "configId": 27,
        "roleId": role_id,
        "mode": voice_mode,
        "voiceId": "",
        "referenceAudioPath": "",
        "referenceText": "",
        "promptText": prompt_text,
        "mixVoices": []
    }

    result = api_call('/voice/generateBindingVoice', payload)

    if result.get('code') == 200:
        data = result.get('data', {})
        audio_path = data.get('audioPath', '')
        audio_url = data.get('audioUrl', '')
        custom_voice_id = data.get('customVoiceId', '')
        reference_text = data.get('referenceText', '')
        
        print(f"  ✅ 成功!")
        print(f"     audioPath: {audio_path}")
        print(f"     customVoiceId: {custom_voice_id}")
        return {
            'role_id': role_id,
            'role_name': role_name,
            'success': True,
            'audio_path': audio_path,
            'audio_url': audio_url,
            'custom_voice_id': custom_voice_id,
            'reference_text': reference_text
        }
    else:
        print(f"  ❌ 失败: {result.get('message', '未知错误')}")
        return {
            'role_id': role_id,
            'role_name': role_name,
            'success': False,
            'error': result.get('message', '未知错误')
        }

def update_world_settings(voice_results):
    """更新世界设置中的音色信息"""
    print("\n正在更新世界设置...")
    
    # 获取当前世界设置
    world_data = get_world_settings()
    if not world_data:
        print("  ❌ 无法获取世界设置")
        return False
    
    # 解析settings
    settings = world_data.get('settings', '{}')
    if isinstance(settings, str):
        settings = json.loads(settings)
    
    # 关键：添加worldId字段（API需要这个字段才能正确更新）
    world_data['worldId'] = world_data.get('id')
    
    # 创建voice_id到audio_path的映射
    voice_map = {r['role_id']: r for r in voice_results if r['success']}
    
    # 更新每个角色的音色信息
    roles = settings.get('roles', [])
    updated_count = 0
    for role in roles:
        role_id = role.get('id', '')
        if role_id in voice_map:
            voice_info = voice_map[role_id]
            # 更新正确的字段
            role['voiceReferenceAudioPath'] = voice_info['audio_path']
            role['voiceReferenceAudioName'] = voice_info['audio_path'].split('/')[-1]
            role['voiceReferenceText'] = voice_info.get('reference_text', '')
            role['voicePresetId'] = voice_info.get('custom_voice_id', '')
            print(f"  ✅ 更新【{role.get('name', role_id)}】")
            updated_count += 1
    
    print(f"  更新了 {updated_count} 个角色的音色")
    
    # 保存世界设置
    world_data['settings'] = json.dumps(settings, ensure_ascii=False)
    
    save_result = api_call('/game/saveWorld', world_data)
    if save_result.get('code') == 200:
        print("  ✅ 世界设置保存成功")
        return True
    else:
        print(f"  ❌ 世界设置保存失败: {save_result.get('message')}")
        return False

def main():
    print("=" * 60)
    print("批量生成角色音色（修复版）")
    print("=" * 60)

    # 获取所有角色
    roles = get_roles()
    print(f"\n获取到 {len(roles)} 个角色")

    # 收集结果
    results = []

    # 逐个生成音色
    for i, role in enumerate(roles, 1):
        print(f"\n[{i}/{len(roles)}] 处理角色...")
        result = generate_voice_for_role(role)
        results.append(result)

        # 每次生成后等待一下
        if i < len(roles):
            print("  等待2秒...")
            time.sleep(2)

    # 打印汇总
    print("\n" + "=" * 60)
    print("音色生成结果汇总")
    print("=" * 60)

    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count

    print(f"\n成功: {success_count}/{len(results)}")
    print(f"失败: {fail_count}/{len(results)}")

    print("\n详细结果:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        if r['success']:
            print(f"  {status} {r['role_name']}: {r.get('audio_path', 'N/A')}")
        else:
            print(f"  {status} {r['role_name']}: {r.get('error', '未知错误')}")

    # 更新世界设置
    if success_count > 0:
        update_world_settings(results)

    # 保存结果到JSON
    output_file = 'api_help/voice_generation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': fail_count
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到: {output_file}")

if __name__ == '__main__':
    main()