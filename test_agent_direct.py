import requests
import json

# Test the agent API directly to see what it returns
agent_url = 'http://localhost:8886/api/agent/chat'

payload = {
    "message": "Hello bot! How are you?",
    "session_id": "test-session-123",
    "user_id": "test-user-123"
}

headers = {'Content-Type': 'application/json'}

print("=" * 60)
print("TESTING AGENT API DIRECTLY")
print("=" * 60)
print(f"URL: {agent_url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(agent_url, json=payload, headers=headers, timeout=10)
    print(f'\n✅ Status Code: {response.status_code}')
    print(f'\n📝 Response:')
    resp_data = response.json()
    print(json.dumps(resp_data, indent=2))
except Exception as e:
    print(f'❌ Error: {e}')
