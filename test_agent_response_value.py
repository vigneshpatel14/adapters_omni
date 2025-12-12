import requests
import json

# Test what the agent returns for our message
agent_url = 'http://localhost:8886/api/agent/chat'

payload = {
    "message": "[Balaji]: Trace test message to check Evolution send",
    "session_id": "test-session-balaji",
    "session_name": "whatsapp-test_917396804318",
    "user_id": "917396804318"
}

headers = {'Content-Type': 'application/json'}

print("=" * 70)
print("TESTING AGENT RESPONSE FOR MESSAGE")
print("=" * 70)
print(f"Message: {payload['message']}")

try:
    response = requests.post(agent_url, json=payload, headers=headers, timeout=10)
    print(f'\nStatus Code: {response.status_code}')
    resp_data = response.json()
    print(f'\nResponse:')
    print(json.dumps(resp_data, indent=2))
    
    # Check the text/message field
    text = resp_data.get('text') or resp_data.get('message')
    print(f'\n📝 Text/Message field value:')
    print(f'   "{text}"')
    print(f'   Length: {len(text) if text else 0}')
    
except Exception as e:
    print(f'Error: {e}')

print("\n" + "=" * 70)
