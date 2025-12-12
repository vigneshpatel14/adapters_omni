#!/usr/bin/env python
"""Check Evolution API instance for QR code"""
import requests
import json
import time

instance_name = "whatsapp-test"
evolution_url = "https://evolution-api-production-7611.up.railway.app"
api_key = "88B2F8C2-5098-455A-AA70-BA84B33FA492"

print("=" * 70)
print("Evolution API Instance Status & QR Code")
print("=" * 70)

headers = {"apikey": api_key}

# After logout, the instance should request a new QR code
# Let's check the current state
url = f"{evolution_url}/instance/connectionState/{instance_name}"
resp = requests.get(url, headers=headers)

print(f"\nInstance Status after logout:")
print(f"Status Code: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    print(json.dumps(data, indent=2)[:1000])
    
    # Check if there's QR code in response
    if "qrcode" in data:
        print(f"\n📱 QR Code available!")
        print(f"   Length: {len(data['qrcode'])}")
    elif "instance" in data and "qrcode" in data["instance"]:
        print(f"\n📱 QR Code available!")

print(f"\n📌 Important:")
print(f"   - Go to Evolution API Manager: {evolution_url}/manager")
print(f"   - Find the 'whatsapp-test' instance")
print(f"   - Look for QR code or connection status")
print(f"   - You may need to scan a NEW QR code to reconnect WhatsApp")
print(f"   - This is because the previous session was logged out (401 error)")
