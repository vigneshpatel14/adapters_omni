#!/usr/bin/env python
"""Check Evolution API instance status"""
import requests
import json

instance_name = "whatsapp-test"
evolution_url = "https://evolution-api-production-7611.up.railway.app"
api_key = "88B2F8C2-5098-455A-AA70-BA84B33FA492"

print("=" * 70)
print("Checking Evolution API Instance Status")
print("=" * 70)

headers = {"apikey": api_key}

try:
    # Check connection state
    url = f"{evolution_url}/instance/connectionState/{instance_name}"
    resp = requests.get(url, headers=headers)
    
    print(f"\nInstance: {instance_name}")
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nConnection Status:")
        print(json.dumps(data, indent=2))
        
        instance_state = data.get("instance", {}).get("state")
        print(f"\n🔍 Connection State: {instance_state}")
        
        if instance_state == "open":
            print("✅ Instance is CONNECTED to WhatsApp")
        elif instance_state == "connecting":
            print("⏳ Instance is CONNECTING to WhatsApp...")
        else:
            print(f"❌ Instance is NOT CONNECTED (state: {instance_state})")
            print("\nWhy messages aren't being received:")
            print("  - The instance needs to be connected to WhatsApp")
            print("  - Typically requires QR code scanning")
            print("  - Check the Evolution API manager UI:")
            print("    https://evolution-api-production-7611.up.railway.app/manager")
    else:
        print(f"Error: {resp.json()}")
        
except Exception as e:
    print(f"Error: {e}")
