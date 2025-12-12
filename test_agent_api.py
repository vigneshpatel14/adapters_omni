import requests
import json

# Test the agent API directly
agent_url = 'http://localhost:8886/api/v1/agent/default/run'

payload = {
    "user_id": "test_user_123",
    "message": "Hello, how are you?",
    "session_name": "test_session",
    "message_type": "text"
}

headers = {'Content-Type': 'application/json'}

print("Testing Agent API...")
print(f"URL: {agent_url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(agent_url, json=payload, headers=headers, timeout=10)
    print(f'\nStatus Code: {response.status_code}')
    print(f'Response: {json.dumps(response.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')
