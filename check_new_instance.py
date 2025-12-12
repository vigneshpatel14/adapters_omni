#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:8882/api/v1/instances'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

try:
    resp = requests.get(url, headers=headers, timeout=5)
    instances = resp.json()
    
    print("=" * 60)
    print("ALL INSTANCES CONFIGURATION")
    print("=" * 60)
    
    for inst in instances:
        print(f"\nInstance: {inst.get('name', 'UNKNOWN')}")
        print(f"  ID: {inst.get('id', 'N/A')}")
        print(f"  Agent API URL: {inst.get('agent_api_url', 'NOT SET')}")
        print(f"  Agent API Key: {inst.get('agent_api_key', 'NOT SET')}")
        print(f"  Evolution Instance: {inst.get('evolution_instance_name', 'NOT SET')}")
        print(f"  Webhook URL: {inst.get('webhook_url', 'NOT SET')}")
        
except Exception as e:
    print(f"Error: {e}")
