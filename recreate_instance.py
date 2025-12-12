#!/usr/bin/env python
"""Delete and recreate the WhatsApp instance to force fresh connection"""
import requests
import json
import time

instance_name = "whatsapp-test"
evolution_url = "https://evolution-api-production-7611.up.railway.app"
api_key = "88B2F8C2-5098-455A-AA70-BA84B33FA492"

headers = {"apikey": api_key}

print("=" * 70)
print("Deleting and Recreating WhatsApp Instance")
print("=" * 70)

print(f"\nInstance: {instance_name}")
print(f"This will:")
print(f"  1. Delete the current instance")
print(f"  2. Wait a moment")
print(f"  3. Create a new fresh instance with new QR code")

# Delete existing instance
print(f"\n🗑️  Deleting instance...")
delete_url = f"{evolution_url}/instance/delete/{instance_name}"
resp = requests.delete(delete_url, headers=headers)
print(f"   Status: {resp.status_code}")

if resp.status_code in [200, 204]:
    print(f"   ✅ Instance deleted")
else:
    print(f"   Response: {resp.json()}")

# Wait
time.sleep(2)

# Create new instance
print(f"\n📱 Creating new instance...")
create_url = f"{evolution_url}/instance/create"

payload = {
    "instanceName": instance_name,
    "integration": "WHATSAPP-BAILEYS",
    "qrcode": True,
    "number": None,
    "businessId": None
}

resp = requests.post(create_url, headers=headers, json=payload)
print(f"   Status: {resp.status_code}")

if resp.status_code in [200, 201]:
    data = resp.json()
    print(f"   ✅ Instance created")
    
    # Extract QR code if present
    if "qrcode" in data:
        print(f"\n   📱 QR Code (base64): {data['qrcode'][:50]}...")
    elif "response" in data and "qrcode" in data.get("response", {}):
        print(f"\n   📱 QR Code available in response")
    else:
        print(f"\n   Response: {json.dumps(data, indent=2)[:500]}")
else:
    print(f"   ❌ Error: {resp.json()}")

print(f"\n" + "=" * 70)
print(f"Next steps:")
print(f"1. Go to: https://evolution-api-production-7611.up.railway.app/manager")
print(f"2. Find the '{instance_name}' instance")
print(f"3. Scan the new QR code with WhatsApp")
print(f"4. Once connected, send a test message")
print(f"=" * 70)
