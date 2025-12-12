#!/usr/bin/env python3
"""
Test webhook with Base64-encoded payload (as Evolution API v2.3.7 sends with "Webhook Base64: Enabled")
"""
import requests
import json
import base64

webhook_url = 'http://localhost:8882/webhook/evolution/whatsapp-test'

# The actual message payload
payload = {
    "event": "messages.upsert",
    "data": {
        "messages": [
            {
                "key": {
                    "remoteJid": "917396804318@s.whatsapp.net",
                    "id": "AAAAH7RXtest==",
                    "fromMe": False
                },
                "message": {
                    "conversation": "hello from base64"
                },
                "messageTimestamp": 1733811188,
                "pushName": "Balaji",
                "status": "PENDING"
            }
        ]
    }
}

# Convert to JSON and then Base64 encode (as Evolution API does)
payload_json = json.dumps(payload["data"])
payload_b64 = base64.b64encode(payload_json.encode()).decode()

print('=== PAYLOAD ===')
print('Original:', json.dumps(payload, indent=2))
print('\n=== BASE64 ENCODED WEBHOOK ===')
webhook_payload = {
    "event": "messages.upsert",
    "data": payload_b64
}
print(f'Sending Base64-encoded data: {payload_b64[:100]}...')

# Send the Base64-encoded webhook
headers = {'Content-Type': 'application/json'}
resp = requests.post(webhook_url, json=webhook_payload, headers=headers)
print(f'\n=== RESPONSE ===')
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:500]}')

# Check the trace
print('\n=== CHECKING TRACE ===')
if resp.status_code == 200:
    import time
    time.sleep(1)  # Wait for processing
    
    try:
        response_data = resp.json()
        trace_id = response_data.get('trace_id')
        if trace_id:
            url = f'http://localhost:8882/api/v1/traces/{trace_id}'
            headers = {'x-api-key': 'omni-dev-key-test-2025'}
            resp = requests.get(url, headers=headers)
            trace = resp.json()
            print(f'Trace ID: {trace.get("trace_id")}')
            print(f'Status: {trace.get("status")}')
            print(f'Sender: {trace.get("sender_phone")}')
            print(f'Message Type: {trace.get("message_type")}')
            print(f'Agent Response: {trace.get("agent_response_success")}')
            print(f'Evolution Success: {trace.get("evolution_success")}')
    except:
        pass
