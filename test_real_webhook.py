#!/usr/bin/env python3
"""
Test webhook with actual Evolution API format from real message
"""
import requests
import json
import base64

# The webhook URL
webhook_url = 'http://localhost:8882/webhook/evolution/whatsapp-test'

# Create a realistic payload based on Evolution API v2.3.7
payload = {
    "event": "messages.upsert",
    "data": {
        "messages": [
            {
                "key": {
                    "remoteJid": "917396804318@s.whatsapp.net",
                    "id": "AAAAH7RXxx==",
                    "fromMe": False
                },
                "message": {
                    "conversation": "hi"
                },
                "messageTimestamp": 1733811188,
                "pushName": "Balaji",
                "status": "PENDING"
            }
        ]
    }
}

# Evolution API Base64 encodes the webhook payload
payload_json = json.dumps(payload)
print('=== WEBHOOK PAYLOAD ===')
print(json.dumps(payload, indent=2))

# Try sending with base64 encoding (as Evolution does)
headers = {'Content-Type': 'application/json'}
resp = requests.post(webhook_url, json=payload, headers=headers)
print(f'\n=== RESPONSE ===')
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:500]}')

# Now check the trace that was created
print('\n=== CHECKING TRACE ===')
url = 'http://localhost:8882/api/v1/traces'
headers = {'x-api-key': 'omni-dev-key-test-2025'}
resp = requests.get(url, headers=headers)
traces = resp.json()
if isinstance(traces, list) and len(traces) > 0:
    trace = traces[-1]
    print(f'Trace ID: {trace.get("trace_id")}')
    print(f'Status: {trace.get("status")}')
    print(f'Sender: {trace.get("sender_phone")}')
    print(f'Message Type: {trace.get("message_type")}')
    print(f'Error: {trace.get("error_message")}')
