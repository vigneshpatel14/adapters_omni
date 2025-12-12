import requests
import json

# Check what instance is configured locally
print("=" * 70)
print("CHECKING LOCAL INSTANCE CONFIGURATION")
print("=" * 70)

url = 'http://localhost:8882/api/v1/instances'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

try:
    response = requests.get(url, headers=headers)
    instances = response.json()
    
    if instances:
        instance = instances[0]
        print(f"\n✅ Found instance:")
        print(f"   ID: {instance.get('id')}")
        print(f"   Name: {instance.get('name')}")
        print(f"   Channel Type: {instance.get('channel_type')}")
        print(f"   Evolution URL: {instance.get('evolution_url')}")
        print(f"   Evolution Key: {instance.get('evolution_key', 'N/A')}")
        print(f"   WhatsApp Instance: {instance.get('whatsapp_instance')}")
        print(f"   Agent API URL: {instance.get('agent_api_url')}")
        print(f"   Default Agent: {instance.get('default_agent')}")
        
        # Now check if we're sending to the right Evolution API
        print(f"\n📊 Analysis:")
        print(f"   Evolution server: {instance.get('evolution_url')}")
        print(f"   Instance name: {instance.get('whatsapp_instance')}")
        print(f"   API Key: {instance.get('evolution_key', 'N/A')[:10]}..." if instance.get('evolution_key') else "   API Key: Not set")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
