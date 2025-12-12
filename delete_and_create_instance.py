#!/usr/bin/env python
"""Delete existing instance and create a new one"""
import requests

omni_url = 'http://localhost:8882'
api_key = 'omni-dev-key-test-2025'

headers = {'x-api-key': api_key}

print("=" * 70)
print("Deleting Existing Instance")
print("=" * 70)

# Get instances
resp = requests.get(f'{omni_url}/api/v1/instances', headers=headers)
instances = resp.json()

print(f'\nFound {len(instances)} instance(s)')

for inst in instances:
    inst_name = inst.get('name')
    inst_id = inst.get('id')
    print(f'\nDeleting: {inst_name}')
    
    # Delete the instance
    delete_resp = requests.delete(f'{omni_url}/api/v1/instances/{inst_id}', headers=headers)
    print(f'  Status: {delete_resp.status_code}')
    
    if delete_resp.status_code == 200:
        print(f'  ✅ Deleted successfully')
    else:
        print(f'  Error: {delete_resp.text[:200]}')

print("\n" + "=" * 70)
print("Creating New Instance")
print("=" * 70)

# Now create the new instance
instance_config = {
    "name": "whatsapp-test",
    "channel_type": "whatsapp",
    "evolution_url": "https://evolution-api-production-7611.up.railway.app",
    "evolution_key": "88B2F8C2-5098-455A-AA70-BA84B33FA492",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "echo-test-key",
    "default_agent": "echo",
    "webhook_base64": True,
    "auto_qr": True,
}

print(f'\nCreating instance: {instance_config["name"]}')

resp = requests.post(f'{omni_url}/api/v1/instances', json=instance_config, headers=headers)

print(f'Status: {resp.status_code}')

if resp.status_code in [200, 201]:
    data = resp.json()
    print(f'\n✅ Instance created successfully!')
    print(f'\n📱 Next Steps:')
    print(f'   1. Go to: https://evolution-api-production-7611.up.railway.app/manager')
    print(f'   2. Find instance: {instance_config["name"]}')
    print(f'   3. Scan the QR code with WhatsApp')
    print(f'   4. Once connected, send a test message')
else:
    print(f'\n❌ Error: {resp.text[:500]}')
