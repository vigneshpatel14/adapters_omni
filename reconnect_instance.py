#!/usr/bin/env python
"""Try to reconnect the Evolution API instance"""
import requests
import json

instance_name = "whatsapp-test"
evolution_url = "https://evolution-api-production-7611.up.railway.app"
api_key = "88B2F8C2-5098-455A-AA70-BA84B33FA492"

print("=" * 70)
print("Reconnecting Evolution API Instance to WhatsApp")
print("=" * 70)

headers = {"apikey": api_key}

try:
    # Try to reconnect/restart the instance
    url = f"{evolution_url}/instance/connect/{instance_name}"
    resp = requests.get(url, headers=headers)
    
    print(f"\n📡 Attempting to reconnect instance...")
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"\n✅ Reconnection initiated!")
        print(json.dumps(data, indent=2)[:1000])
        
        # Check for QR code
        if "qrcode" in data:
            print(f"\n📱 QR Code provided (base64):")
            print(f"Length: {len(data['qrcode'])} characters")
            print(f"You need to scan this QR code in WhatsApp to reconnect the instance")
        elif "response" in data and isinstance(data["response"], dict):
            if "qrcode" in data["response"]:
                print(f"\n📱 QR Code in response")
    else:
        print(f"\n⚠️ Response:")
        print(json.dumps(resp.json(), indent=2)[:1000])
        
except Exception as e:
    print(f"Error: {e}")
