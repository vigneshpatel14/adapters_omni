#!/usr/bin/env python
"""Set webhook for Evolution API instance"""
import requests
import json

instance_name = "whatsapp-test"
evolution_url = "https://evolution-api-production-7611.up.railway.app"
api_key = "88B2F8C2-5098-455A-AA70-BA84B33FA492"

# Your public IP or domain - this is what Evolution API will call when messages arrive
webhook_url = "http://172.16.141.205:8882/webhook/evolution/whatsapp-test"

print("=" * 70)
print("Setting Webhook for Evolution API Instance")
print("=" * 70)

print(f"\nInstance: {instance_name}")
print(f"Webhook URL: {webhook_url}")
print(f"Events: ['MESSAGES_UPSERT']")
print(f"Base64 Encoding: Enabled")

headers = {"apikey": api_key, "Content-Type": "application/json"}

webhook_payload = {
    "webhook": {
        "enabled": True,
        "url": webhook_url,
        "events": ["MESSAGES_UPSERT"],
        "base64": True,
        "byEvents": False
    }
}

try:
    # Set webhook
    url = f"{evolution_url}/webhook/set/{instance_name}"
    resp = requests.post(url, headers=headers, json=webhook_payload)
    
    print(f"\n🔧 Setting webhook...")
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"\n✅ SUCCESS!")
        print(f"Response: {json.dumps(data, indent=2)[:500]}")
        print(f"\n✅ Webhook is now configured!")
        print(f"   Evolution API will send incoming messages to: {webhook_url}")
    else:
        print(f"\n❌ Failed to set webhook")
        print(f"Response: {resp.text}")
        
except Exception as e:
    print(f"Error: {e}")
