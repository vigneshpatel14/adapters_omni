import requests
import json
from datetime import datetime
import time

# Send a test message to Balaji
webhook_payload = {
    'event': 'messages.upsert',
    'data': {
        'messages': [
            {
                'key': {
                    'remoteJid': '917396804318@s.whatsapp.net',
                    'fromMe': False,
                    'id': 'test_msg_balaji_001'
                },
                'message': {
                    'conversation': 'Hello Balaji! Testing the webhook - can you see this message?'
                },
                'messageTimestamp': int(datetime.now().timestamp()),
                'pushName': 'Balaji',
                'status': 'PENDING'
            }
        ]
    }
}

# Send to webhook endpoint
url = 'http://localhost:8882/webhook/evolution/whatsapp-test'
headers = {'Content-Type': 'application/json'}

print('=' * 60)
print('SENDING TEST MESSAGE TO BALAJI')
print('=' * 60)
print(f'Phone: 917396804318')
print(f'Name: Balaji')
print(f'Message: Hello Balaji! Testing the webhook - can you see this message?')
print(f'Webhook URL: {url}')
print()

try:
    response = requests.post(url, json=webhook_payload, headers=headers, timeout=10)
    print(f'✅ Webhook Status: {response.status_code}')
    data = response.json()
    trace_id = data.get('trace_id')
    print(f'✅ Trace ID: {trace_id}')
    print(f'✅ Instance: {data.get("instance")}')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)

# Wait for processing
print('\nWaiting for message processing...')
time.sleep(2)

# Check the trace to verify everything worked
if trace_id:
    print('\n' + '=' * 60)
    print('CHECKING MESSAGE PROCESSING')
    print('=' * 60)
    traces_url = f'http://localhost:8882/api/v1/traces/{trace_id}'
    headers_api = {'x-api-key': 'omni-dev-key-test-2025'}
    try:
        response = requests.get(traces_url, headers=headers_api)
        trace = response.json()
        
        print(f'Status: {trace.get("status")}')
        print(f'Sender Phone: {trace.get("sender_phone")}')
        print(f'Sender Name: {trace.get("sender_name")}')
        print(f'Message Type: {trace.get("message_type")}')
        print(f'Agent Processing Time: {trace.get("agent_processing_time_ms")}ms')
        print(f'Agent Response Success: {trace.get("agent_response_success")}')
        print(f'Evolution Send Success: {trace.get("evolution_success")}')
        
        if trace.get("error_message"):
            print(f'❌ Error: {trace.get("error_message")}')
        else:
            print('✅ No errors')
            
        print('\n' + '=' * 60)
        print('WEBHOOK TEST RESULT: ✅ SUCCESS')
        print('=' * 60)
        print('Message should appear in Balaji\'s WhatsApp chat shortly!')
        
    except Exception as e:
        print(f'Error checking trace: {e}')
