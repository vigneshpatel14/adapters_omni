import requests
import json

# The user provided the URL, let's extract the instance ID and phone
# https://evolution-api-production-7611.up.railway.app/manager/instance/1020a32a-a8db-4268-82a8-84eb409637c1/chat/917396804318@s.whatsapp.net

evolution_url = "https://evolution-api-production-7611.up.railway.app"
instance_id = "1020a32a-a8db-4268-82a8-84eb409637c1"
phone = "917396804318"

# Get instance details first
print("=" * 70)
print("CHECKING EVOLUTION API INSTANCE & MESSAGES")
print("=" * 70)

# Check instance status
instance_url = f"{evolution_url}/api/v1/instances/{instance_id}"
print(f"\n[1] Checking instance status...")
print(f"    URL: {instance_url}")

try:
    response = requests.get(instance_url, timeout=5)
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        instance = response.json()
        print(f"    Instance exists: {instance.get('instance', {}).get('name', 'unknown')}")
        print(f"    Connected: {instance.get('instance', {}).get('connected', 'unknown')}")
    else:
        print(f"    Response: {response.text[:200]}")
except Exception as e:
    print(f"    Error: {e}")

# Check messages/chats
messages_url = f"{evolution_url}/api/v1/instances/{instance_id}/chats"
print(f"\n[2] Checking chats...")
print(f"    URL: {messages_url}")

try:
    response = requests.get(messages_url, timeout=5)
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        chats = response.json()
        print(f"    Total chats: {len(chats) if isinstance(chats, list) else 'unknown'}")
        # Look for our target phone
        for chat in chats if isinstance(chats, list) else []:
            if "917396804318" in str(chat.get("id", "")):
                print(f"    ✅ Found chat with target phone!")
                print(f"       Chat ID: {chat.get('id')}")
                print(f"       Name: {chat.get('name')}")
except Exception as e:
    print(f"    Error: {e}")

# Check specific chat messages
messages_detail_url = f"{evolution_url}/api/v1/instances/{instance_id}/messages/{phone}@s.whatsapp.net"
print(f"\n[3] Checking messages with target phone...")
print(f"    URL: {messages_detail_url}")

try:
    response = requests.get(messages_detail_url, timeout=5)
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        messages = response.json()
        print(f"    Response type: {type(messages)}")
        if isinstance(messages, dict):
            print(f"    Response keys: {list(messages.keys())}")
            # Print messages info
            msgs = messages.get('messages', messages.get('data', []))
            if msgs:
                print(f"    Total messages: {len(msgs)}")
                print(f"\n    Recent messages:")
                for i, msg in enumerate(msgs[-5:]):  # Last 5 messages
                    print(f"      {i+1}. From: {msg.get('from', 'unknown')}")
                    print(f"         Text: {msg.get('text', 'N/A')[:50]}...")
                    print(f"         Status: {msg.get('status', 'unknown')}")
        else:
            print(f"    Response: {str(messages)[:300]}")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "=" * 70)
