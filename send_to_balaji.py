#!/usr/bin/env python
"""Send a test message to Balaji"""
import requests
import json
import base64
import time

# Webhook payload for Balaji
message = {
    'key': {
        'remoteJid': '917396804318@s.whatsapp.net',
        'fromMe': False,
        'id': 'test_balaji_1765375900'
    },
    'messageTimestamp': 1765375900,
    'pushName': 'Balaji',
    'status': 'PENDING',
    'message': {
        'conversation': 'Hey Balaji! The webhook system is working perfectly now. You should see this message on WhatsApp!'
    }
}

# Encode as base64
payload_json = json.dumps(message)
payload_b64 = base64.b64encode(payload_json.encode()).decode()

webhook_payload = {'data': payload_b64}

# Send webhook
url = 'http://localhost:8882/webhook/evolution/whatsapp-test'
print("=== Sending message to Balaji ===\n")
resp = requests.post(url, json=webhook_payload)
print(f'✅ Webhook Status: {resp.status_code}')

if resp.status_code == 200:
    trace_id = resp.json().get('trace_id')
    print(f'   Trace ID: {trace_id}')
    
    # Wait for processing
    print("\n⏳ Waiting for processing...")
    time.sleep(3)
    
    # Get trace
    trace_url = 'http://localhost:8882/api/v1/traces'
    headers = {'x-api-key': 'omni-dev-key-test-2025'}
    resp = requests.get(trace_url, headers=headers)
    traces = resp.json()
    
    if traces:
        t = traces[0]
        print(f'\n✅ Message Status: {t.get("status")}')
        print(f'   Sender: {t.get("sender_name")}')
        print(f'   Evolution Success: {t.get("evolution_success")}')
        print(f'\n📱 Message delivered to Balaji!')
