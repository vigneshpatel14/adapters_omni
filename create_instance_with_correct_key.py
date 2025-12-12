#!/usr/bin/env python
"""Create a new WhatsApp instance with correct Evolution API key"""
import requests
import json

omni_url = 'http://localhost:8882'
omni_api_key = 'omni-dev-key-test-2025'
evolution_url = 'https://evolution-api-production-7611.up.railway.app'
evolution_key = 'VigneshKey17'

print("=" * 70)
print("Creating New WhatsApp Instance")
print("=" * 70)

headers = {'x-api-key': omni_api_key}

# Instance configuration
instance_config = {
    "name": "whatsapp-bot",
    "channel_type": "whatsapp",
    "evolution_url": evolution_url,
    "evolution_key": evolution_key,
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "echo-test-key",
    "default_agent": "echo",
    "webhook_base64": True,
    "auto_qr": True,
}

print(f'\n📝 Creating instance: {instance_config["name"]}')
print(f'   Evolution API: {evolution_url}')
print(f'   Evolution Key: VigneshKey17')
print(f'   Agent API: {instance_config["agent_api_url"]}')

try:
    resp = requests.post(
        f'{omni_url}/api/v1/instances',
        json=instance_config,
        headers=headers,
        timeout=30
    )
    
    print(f'\n📡 Response Status: {resp.status_code}')
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f'\n✅ Instance created successfully!')
        
        instance_id = data.get('id')
        instance_name = data.get('name')
        evolution_instance = data.get('whatsapp_instance')
        
        print(f'\n📋 Instance Details:')
        print(f'   Name: {instance_name}')
        print(f'   ID: {instance_id}')
        print(f'   Evolution Instance: {evolution_instance}')
        
        print(f'\n🔑 Next Steps:')
        print(f'   1. Go to: {evolution_url}/manager/')
        print(f'   2. Find instance: {instance_name}')
        print(f'   3. Scan the QR code with WhatsApp')
        print(f'   4. Once connected, send a test message')
        
    else:
        print(f'\n❌ Error creating instance')
        error_data = resp.json()
        print(json.dumps(error_data, indent=2))
        
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
