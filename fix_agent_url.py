#!/usr/bin/env python3
import requests

url = 'http://localhost:8882/api/v1/instances/whatsapp-bot'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

# Update with 127.0.0.1 (localhost loopback) which won't be converted
update_data = {
    'agent_api_url': 'http://127.0.0.1:8886'
}

resp = requests.put(url, json=update_data, headers=headers, timeout=10)

print(f"Status: {resp.status_code}")
print(f"Agent API URL updated to: http://127.0.0.1:8886")

# Verify
resp = requests.get(url, headers=headers, timeout=5)
data = resp.json()
print(f"Confirmed in DB: {data.get('agent_api_url')}")
