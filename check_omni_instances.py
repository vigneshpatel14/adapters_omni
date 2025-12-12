#!/usr/bin/env python
"""Check instances in Omni"""
import requests

omni_url = 'http://localhost:8882'
api_key = 'omni-dev-key-test-2025'

headers = {'x-api-key': api_key}

print("=" * 70)
print("Checking Instances in Omni")
print("=" * 70)

# Get instances from Omni
resp = requests.get(f'{omni_url}/api/v1/instances', headers=headers, timeout=5)

print(f'\nStatus: {resp.status_code}')

if resp.status_code == 200:
    instances = resp.json()
    print(f'\nFound {len(instances)} instance(s) in Omni:')
    
    if instances:
        for inst in instances:
            print(f'\n  Name: {inst.get("name")}')
            print(f'  ID: {inst.get("id")}')
            print(f'  Evolution Instance: {inst.get("whatsapp_instance")}')
            print(f'  Channel: {inst.get("channel_type")}')
    else:
        print("  (No instances)")
else:
    print(f'Error: {resp.text}')
