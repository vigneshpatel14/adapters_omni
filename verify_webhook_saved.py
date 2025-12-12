#!/usr/bin/env python
"""Verify webhook is saved in Evolution API"""
import requests
import json

instance_name = "whatsapp-test"
evolution_url = "https://evolution-api-production-7611.up.railway.app"
api_key = "88B2F8C2-5098-455A-AA70-BA84B33FA492"

print("=" * 70)
print("Verifying Webhook Configuration in Evolution API")
print("=" * 70)

headers = {"apikey": api_key}

try:
    # Fetch all instances to see webhook config
    url = f"{evolution_url}/instance/fetchInstances"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nSearching for instance: {instance_name}")
        
        if isinstance(data, list):
            for inst in data:
                if inst.get("name") == instance_name:
                    print(f"✅ Found instance")
                    print(f"\nFull instance data (relevant parts):")
                    print(f"  Name: {inst.get('name')}")
                    print(f"  Connection Status: {inst.get('connectionStatus')}")
                    print(f"  State: {inst.get('state')}")
                    
                    # Check for webhook configuration in different possible locations
                    print(f"\n🔍 Checking for webhook config...")
                    
                    if "webhook" in inst:
                        webhook = inst["webhook"]
                        print(f"\n✅ Found 'webhook' field:")
                        print(f"  Enabled: {webhook.get('enabled')}")
                        print(f"  URL: {webhook.get('url')}")
                        print(f"  Events: {webhook.get('events')}")
                    elif "Webhook" in inst:
                        webhook = inst["Webhook"]
                        print(f"\n✅ Found 'Webhook' field:")
                        print(json.dumps(webhook, indent=2)[:500])
                    else:
                        print(f"\n❌ No webhook field found in instance!")
                        print(f"\nAvailable fields: {list(inst.keys())}")
                    
                    # Print full instance data for debugging
                    print(f"\n📋 Full instance (first 1500 chars):")
                    print(json.dumps(inst, indent=2)[:1500])
                    break
        else:
            print(f"Unexpected response format: {type(data)}")
    else:
        print(f"Error: {resp.json()}")
        
except Exception as e:
    print(f"Error: {e}")
