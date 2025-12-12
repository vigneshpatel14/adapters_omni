#!/usr/bin/env python
"""Check Evolution API instance webhook configuration"""
import requests
import json

instance_name = "whatsapp-test"
evolution_url = "https://evolution-api-production-7611.up.railway.app"
api_key = "88B2F8C2-5098-455A-AA70-BA84B33FA492"

print("=" * 70)
print("Checking Evolution API Instance Webhook Configuration")
print("=" * 70)

headers = {"apikey": api_key}

try:
    # Fetch all instances
    url = f"{evolution_url}/instance/fetchInstances"
    resp = requests.get(url, headers=headers)
    print(f"\nFetch Instances Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nFull response (first 2000 chars):")
        print(json.dumps(data, indent=2)[:2000])
    else:
        print(f"Error: {resp.json()}")
        
except Exception as e:
    print(f"Error: {e}")
