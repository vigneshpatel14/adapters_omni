import requests
import json

# Test the agent API with the correct payload
agent_url = 'http://localhost:8886/api/agent/chat'

payload = {
    "message": "Hello bot! How are you?",
    "session_id": "test-session-123",
    "session_name": "test-session",
    "user_id": "test-user-123"
}

headers = {'Content-Type': 'application/json'}

print("=" * 60)
print("TESTING AGENT API WITH CORRECT PAYLOAD")
print("=" * 60)
print(f"URL: {agent_url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(agent_url, json=payload, headers=headers, timeout=10)
    print(f'\n✅ Status Code: {response.status_code}')
    print(f'\n📝 Full Response:')
    resp_data = response.json()
    print(json.dumps(resp_data, indent=2))
    
    # Check what fields are in the response
    print(f'\n✅ Response contains:')
    for key in resp_data.keys():
        print(f'   - {key}')
except Exception as e:
    print(f'❌ Error: {e}')
