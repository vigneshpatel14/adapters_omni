import requests
import json
from datetime import datetime
import time

# Prepare test webhook data - exactly matching Evolution API format
webhook_payload = {
    'event': 'messages.upsert',
    'data': {
        'messages': [
            {
                'key': {
                    'remoteJid': '919014456421@s.whatsapp.net',
                    'fromMe': False,
                    'id': 'test_msg_001'
                },
                'message': {
                    'conversation': 'Hello, can you help me?'
                },
                'messageTimestamp': int(datetime.now().timestamp()),
                'pushName': 'Vignesh',
                'status': 'PENDING'
            }
        ]
    }
}

# Send to webhook endpoint
url = 'http://localhost:8882/webhook/evolution/whatsapp-test'
headers = {'Content-Type': 'application/json'}

print('Sending message to webhook...')
try:
    response = requests.post(url, json=webhook_payload, headers=headers, timeout=10)
    print(f'Webhook Status Code: {response.status_code}')
    print(f'Webhook Response: {json.dumps(response.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')

# Wait a moment for processing
time.sleep(2)

# Check traces to see if message was processed
print('\nChecking message traces...')
traces_url = 'http://localhost:8882/api/v1/traces'
headers = {'x-api-key': 'omni-dev-key-test-2025'}
try:
    response = requests.get(traces_url, headers=headers)
    traces = response.json()
    print(f'Total traces: {len(traces)}')
    if traces:
        latest = traces[0]
        print(f'Latest trace ID: {latest.get("trace_id")}')
        print(f'Latest trace details:')
        print(f'  - Status: {latest.get("status", "N/A")}')
        print(f'  - Message: {str(latest.get("message", "N/A"))[:100]}')
except Exception as e:
    print(f'Error getting traces: {e}')
