#!/usr/bin/env python
"""Update existing instance and set up webhook"""
import requests
import json

omni_url = 'http://localhost:8882'
api_key = 'omni-dev-key-test-2025'
evolution_url = 'https://evolution-api-production-7611.up.railway.app'
evolution_key = '88B2F8C2-5098-455A-AA70-BA84B33FA492'

headers = {'x-api-key': api_key}

print("=" * 70)
print("Updating Instance Configuration")
print("=" * 70)

# Get the instance
resp = requests.get(f'{omni_url}/api/v1/instances', headers=headers)
instances = resp.json()

if instances:
    inst = instances[0]
    inst_id = inst.get('id')
    inst_name = inst.get('name')
    
    print(f"\nFound instance: {inst_name}")
    
    # Update the instance configuration
    inst['agent_api_url'] = 'http://localhost:8886'
    inst['agent_api_key'] = 'echo-test-key'
    inst['default_agent'] = 'echo'
    inst['webhook_base64'] = True
    inst['auto_qr'] = True
    
    # Update
    update_resp = requests.put(f'{omni_url}/api/v1/instances/{inst_id}', json=inst, headers=headers)
    
    print(f'\nUpdate Status: {update_resp.status_code}')
    if update_resp.status_code == 200:
        print('✅ Instance configuration updated')
        print(f'  Agent URL: {inst.get("agent_api_url")}')
        print(f'  Agent: {inst.get("default_agent")}')
        
        # Now set the webhook in Evolution API
        print("\n" + "=" * 70)
        print("Setting Webhook in Evolution API")
        print("=" * 70)
        
        webhook_url = f"http://172.16.141.205:8882/webhook/evolution/{inst_name}"
        
        evo_headers = {"apikey": evolution_key, "Content-Type": "application/json"}
        webhook_payload = {
            "webhook": {
                "enabled": True,
                "url": webhook_url,
                "events": ["MESSAGES_UPSERT"],
                "base64": True,
                "byEvents": False
            }
        }
        
        evo_url = f"{evolution_url}/webhook/set/{inst_name}"
        evo_resp = requests.post(evo_url, headers=evo_headers, json=webhook_payload)
        
        print(f"\nWebhook Set Status: {evo_resp.status_code}")
        if evo_resp.status_code in [200, 201]:
            print("✅ Webhook configured")
            print(f"  URL: {webhook_url}")
        else:
            print(f"Error: {evo_resp.text[:300]}")
        
        print("\n" + "=" * 70)
        print("📱 Next Steps:")
        print("=" * 70)
        print(f"1. Go to: {evolution_url}/manager")
        print(f"2. Find instance: {inst_name}")
        print(f"3. Scan the QR code with WhatsApp")
        print(f"4. Once connected, send a test message")
        
    else:
        print(f'Error: {update_resp.text[:300]}')
else:
    print("No instances found!")
