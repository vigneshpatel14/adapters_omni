#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:8882/api/v1/instances'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

resp = requests.get(url, headers=headers)
instance = resp.json()[0]
instance_id = instance['id']

print('Current agent URL:', instance['agent_api_url'])

instance['agent_api_url'] = 'http://localhost:8886'

print(f'Instance ID: {instance_id}')
print(f'Instance name: {instance["name"]}')

# Try different endpoint patterns
for endpoint in [
    f'/api/v1/instances/{instance_id}',
    f'/api/instances/{instance_id}',
    f'/api/v1/instances/{instance["name"]}',
]:
    update_url = f'http://localhost:8882{endpoint}'
    resp = requests.put(update_url, json=instance, headers=headers)
    print(f'Trying {endpoint}: Status {resp.status_code}')
    if resp.status_code == 200:
        print('✓ Agent URL updated to: http://localhost:8886')
        break
    elif resp.status_code != 404:
        print('Response:', resp.text[:200])
        break
