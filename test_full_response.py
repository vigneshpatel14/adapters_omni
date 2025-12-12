import requests
import json
from datetime import datetime
import time

# Send a test message with a clear message to get a response
webhook_payload = {
    'event': 'messages.upsert',
    'data': {
        'messages': [
            {
                'key': {
                    'remoteJid': '919014456421@s.whatsapp.net',
                    'fromMe': False,
                    'id': 'test_msg_response_001'
                },
                'message': {
                    'conversation': 'Hello bot, what time is it?'
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

print('Sending test message to webhook...')
try:
    response = requests.post(url, json=webhook_payload, headers=headers, timeout=10)
    print(f'Webhook Status: {response.status_code}')
    data = response.json()
    trace_id = data.get('trace_id')
    print(f'Trace ID: {trace_id}')
    print(f'Response: {json.dumps(data, indent=2)}')
except Exception as e:
    print(f'Error: {e}')

# Wait for processing
time.sleep(3)

# Check the trace to see what happened
if trace_id:
    print('\n=== CHECKING TRACE DETAILS ===')
    traces_url = f'http://localhost:8882/api/v1/traces/{trace_id}'
    headers = {'x-api-key': 'omni-dev-key-test-2025'}
    try:
        response = requests.get(traces_url, headers=headers)
        trace = response.json()
        
        print(f'Status: {trace.get("status")}')
        print(f'Sender: {trace.get("sender_phone")}')
        print(f'Message Type: {trace.get("message_type")}')
        print(f'Agent Processing Time: {trace.get("agent_processing_time_ms")}ms')
        print(f'Evolution Success: {trace.get("evolution_success")}')
        print(f'Agent Response Success: {trace.get("agent_response_success")}')
    except Exception as e:
        print(f'Error: {e}')
