#!/usr/bin/env python
"""Create a new WhatsApp instance"""
import requests
import json

omni_url = "http://localhost:8882"
api_key = "omni-dev-key-test-2025"

print("=" * 70)
print("Creating New WhatsApp Instance")
print("=" * 70)

# Instance configuration
instance_config = {
    "name": "whatsapp-test",
    "channel_type": "whatsapp",
    "evolution_url": "https://evolution-api-production-7611.up.railway.app",
    "evolution_key": "88B2F8C2-5098-455A-AA70-BA84B33FA492",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "echo-test-key",
    "default_agent": "echo",
    "webhook_base64": True,
    "auto_qr": True,
    "is_default": True
}

headers = {
    "x-api-key": api_key,
    "Content-Type": "application/json"
}

try:
    url = f"{omni_url}/api/v1/instances"
    print(f"\n📝 Creating instance: {instance_config['name']}")
    print(f"   Evolution API: {instance_config['evolution_url']}")
    print(f"   Agent API: {instance_config['agent_api_url']}")
    
    resp = requests.post(url, json=instance_config, headers=headers)
    
    print(f"\n📡 Response Status: {resp.status_code}")
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"\n✅ Instance created successfully!")
        
        # Extract important info
        instance_id = data.get("id") or data.get("whatsapp_instance")
        evolution_instance_id = data.get("whatsapp_instance")
        
        print(f"\n📋 Instance Details:")
        print(f"   Name: {data.get('name')}")
        print(f"   Instance ID: {instance_id}")
        print(f"   Evolution Instance: {evolution_instance_id}")
        print(f"   Agent: {data.get('default_agent')}")
        print(f"   Webhook URL: {data.get('webhook_url')}")
        
        print(f"\n🔑 Next Steps:")
        print(f"   1. Go to: https://evolution-api-production-7611.up.railway.app/manager")
        print(f"   2. Find instance: whatsapp-test")
        print(f"   3. Scan QR code with WhatsApp")
        print(f"   4. Once connected, send a test message")
        
        # Save instance info
        with open("instance_info.json", "w") as f:
            json.dump({
                "instance_id": instance_id,
                "name": data.get('name'),
                "evolution_instance": evolution_instance_id,
                "webhook_url": data.get('webhook_url')
            }, f, indent=2)
        
        print(f"\n💾 Instance info saved to instance_info.json")
        
    else:
        print(f"\n❌ Error creating instance")
        print(json.dumps(resp.json(), indent=2))
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
        
except Exception as e:
    print(f"❌ Error: {e}")
