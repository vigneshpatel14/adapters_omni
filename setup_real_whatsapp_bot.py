#!/usr/bin/env python3
"""
Real WhatsApp bot setup - creates Omni instance and configures webhook
"""
import requests
import json
from datetime import datetime

# Configuration
EVOLUTION_API_URL = "https://evolution-api-production-7611.up.railway.app"
EVOLUTION_GLOBAL_KEY = "VigneshKey17"
OMNI_API_URL = "http://localhost:8882"
OMNI_API_KEY = "omni-dev-key-test-2025"
ECHO_AGENT_URL = "http://172.16.141.205:8886"

# Your real WhatsApp instance in Evolution Manager
EVOLUTION_INSTANCE_ID = "1020a32a-a8db-4268-82a8-84eb409637c1"

def get_instance_info():
    """Get info about your existing Evolution instance"""
    print("\n" + "="*70)
    print("CHECKING EVOLUTION INSTANCE")
    print("="*70)
    
    # Try different endpoints to get instance info
    endpoints = [
        f"/instance/{EVOLUTION_INSTANCE_ID}/info",
        f"/api/instance/{EVOLUTION_INSTANCE_ID}/info",
        f"/api/v1/instance/{EVOLUTION_INSTANCE_ID}/info",
    ]
    
    headers = {"apikey": EVOLUTION_GLOBAL_KEY}
    
    for endpoint in endpoints:
        url = EVOLUTION_API_URL + endpoint
        print(f"\nTrying: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"✅ SUCCESS")
                data = resp.json()
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"Response: {resp.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n⚠️  Could not get instance info from Evolution API")
    print(f"Instance ID: {EVOLUTION_INSTANCE_ID}")
    return None

def create_omni_instance():
    """Create Omni instance pointing to your real WhatsApp number"""
    print("\n" + "="*70)
    print("CREATING OMNI INSTANCE")
    print("="*70)
    
    # Create unique instance name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    instance_name = f"whatsapp-bot-{timestamp}"
    
    url = f"{OMNI_API_URL}/api/v1/instances"
    headers = {"x-api-key": OMNI_API_KEY}
    
    payload = {
        "name": instance_name,
        "channel_type": "whatsapp",
        "evolution_url": EVOLUTION_API_URL,
        "evolution_global_key": EVOLUTION_GLOBAL_KEY,
        "evolution_instance_id": EVOLUTION_INSTANCE_ID,
        "agent_api_url": ECHO_AGENT_URL,
        "agent_api_key": "echo-agent-key",
        "default_agent": "echo",
        "webhook_url": f"{OMNI_API_URL}/webhook/evolution/{instance_name}",
        "is_active": True,
    }
    
    print(f"\nURL: {url}")
    print(f"Instance Name: {instance_name}")
    print(f"Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            print(f"\n✅ Instance created successfully!")
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"❌ Failed to create instance")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_omni_instances():
    """List all Omni instances"""
    print("\n" + "="*70)
    print("LISTING OMNI INSTANCES")
    print("="*70)
    
    url = f"{OMNI_API_URL}/api/v1/instances"
    headers = {"x-api-key": OMNI_API_KEY}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Instances ({len(data)}):")
            if data:
                print(json.dumps(data, indent=2))
            else:
                print("No instances found")
            return data
        else:
            print(f"Error: {resp.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    print("\n" + "🤖 "*20)
    print("REAL WHATSAPP BOT SETUP")
    print("🤖 "*20)
    
    # Get existing instance info
    instance_info = get_instance_info()
    
    # Create Omni instance
    omni_instance = create_omni_instance()
    
    if omni_instance:
        instance_name = omni_instance.get("name")
        print(f"\n" + "="*70)
        print("WEBHOOK CONFIGURATION")
        print("="*70)
        print(f"Instance Name: {instance_name}")
        print(f"Webhook URL: {OMNI_API_URL}/webhook/evolution/{instance_name}")
        print(f"\nTo configure webhook in Evolution Manager UI:")
        print(f"1. Go to: {EVOLUTION_API_URL}/manager")
        print(f"2. Select your instance (1020a32a-a8db-4268-82a8-84eb409637c1)")
        print(f"3. Set webhook URL to: {OMNI_API_URL}/webhook/evolution/{instance_name}")
        print(f"4. Save and test")
    
    # List all instances
    list_omni_instances()

if __name__ == "__main__":
    main()
