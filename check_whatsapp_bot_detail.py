#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:8882/api/v1/instances/whatsapp-bot'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

try:
    resp = requests.get(url, headers=headers, timeout=5)
    data = resp.json()
    
    print("=" * 60)
    print("WHATSAPP-BOT INSTANCE CONFIGURATION")
    print("=" * 60)
    print(json.dumps(data, indent=2))
    
except Exception as e:
    print(f"Error: {e}")
