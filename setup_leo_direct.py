#!/usr/bin/env python
"""Test Leo Agent integration by using Leo's URL as agent_api_url"""
import requests
import json

# Configuration
OMNI_URL = 'http://localhost:8882'
OMNI_API_KEY = 'omni-dev-key-test-2025'

# Evolution API Configuration
EVOLUTION_URL = 'https://evolution-api-production-7611.up.railway.app'
EVOLUTION_KEY = 'VigneshKey17'

# Leo's streaming endpoint - Omni will auto-detect and use LeoAgentClient
LEO_API_URL = 'https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1/workflow-engine/e9f65742-8f61-4a7f-b0d2-71b77c5391e7/stream'

print("=" * 70)
print("Testing Leo Agent Integration (Direct URL)")
print("=" * 70)

headers = {'x-api-key': OMNI_API_KEY}

# Instance configuration with Leo's URL as agent_api_url
instance_config = {
    "name": "whatsapp-leo-direct",
    "channel_type": "whatsapp",
    "evolution_url": EVOLUTION_URL,
    "evolution_key": EVOLUTION_KEY,
    "agent_api_url": LEO_API_URL,  # Leo endpoint - triggers LeoAgentClient
    "agent_api_key": "leo_builtin",  # Placeholder - real auth from .env
    "default_agent": "leo",
    "agent_timeout": 120,
    "webhook_base64": True,
    "auto_qr": True,
}

print(f'\n📝 Instance Configuration:')
print(f'   Name: {instance_config["name"]}')
print(f'   Channel: {instance_config["channel_type"]}')
print(f'   Evolution API: {EVOLUTION_URL}')
print(f'   Agent API URL: {LEO_API_URL}')
print(f'   (Omni will detect Leo URL and use built-in normalization)')
print(f'   Agent: Built-in Leo (no adapter needed!)')
print(f'   Agent Timeout: {instance_config["agent_timeout"]}s')

# Create instance
print(f'\n📡 Creating instance in Omni...')
try:
    resp = requests.post(
        f'{OMNI_URL}/api/v1/instances',
        json=instance_config,
        headers=headers,
        timeout=30
    )
    
    print(f'\n📊 Response Status: {resp.status_code}')
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f'✅ Instance created successfully!')
        print(f'\nInstance Details:')
        print(json.dumps(data, indent=2))
        
        # Get QR code
        instance_name = data.get('name') or instance_config['name']
        print(f'\n📱 Fetching QR Code...')
        
        qr_resp = requests.get(
            f'{OMNI_URL}/api/v1/instances/{instance_name}/qr',
            headers=headers,
            timeout=30
        )
        
        if qr_resp.status_code == 200:
            qr_data = qr_resp.json()
            if qr_data.get('qr_code'):
                print(f'✅ QR Code available!')
                print(f'\nScan this QR code with WhatsApp:')
                print(qr_data['qr_code'])
            else:
                print(f'⚠️  QR Code not yet available. Status: {qr_data.get("status")}')
        else:
            print(f'⚠️  Could not fetch QR code: {qr_resp.status_code}')
    else:
        print(f'❌ Failed to create instance')
        print(f'Response: {resp.text}')
        
except Exception as e:
    print(f'❌ Error: {e}')

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("1. Scan the QR code with WhatsApp")
print("2. Send a test message to your WhatsApp number")
print("3. Leo will respond directly (no adapter needed!)")
print("4. Check logs: python -m src")
print("5. Check traces: GET http://localhost:8882/api/v1/traces")
print("=" * 70)
print("\n🎯 Leo is now integrated directly into Omni!")
print("   No separate adapter process needed.")
print("=" * 70)
