#!/usr/bin/env python
"""Send a test message to Pavan"""
import requests
import json
import base64
import time

# Webhook payload for Pavan
message = {
    'key': {
        'remoteJid': '919391189719@s.whatsapp.net',
        'fromMe': False,
        'id': 'test_pavan_1765375800'
    },
    'messageTimestamp': 1765375800,
    'pushName': 'Pavan',
    'status': 'PENDING',
    'message': {
        'conversation': 'Hello Pavan! This is a test message from the webhook system.'
    }
}

# Encode as base64
payload_json = json.dumps(message)
payload_b64 = base64.b64encode(payload_json.encode()).decode()

webhook_payload = {
    'data': payload_b64
}

# Send webhook
url = 'http://localhost:8882/webhook/evolution/whatsapp-bot'
headers = {'Content-Type': 'application/json'}

print("=== Sending message to Pavan ===\n")
resp = requests.post(url, json=webhook_payload, headers=headers)
print(f'✅ Webhook Status: {resp.status_code}')
if resp.status_code == 200:
    resp_data = resp.json()
    print(f'Trace ID: {resp_data.get("trace_id")}')

# Wait for processing
print("\n⏳ Waiting for processing...")
time.sleep(3)

# Get latest trace
trace_url = 'http://localhost:8882/api/v1/traces'
headers = {'x-api-key': 'omni-dev-key-test-2025'}
resp = requests.get(trace_url, headers=headers)
traces = resp.json()

if traces:
    for trace in traces[:1]:
        print(f"\n📊 Trace Details:")
        print(f'  Status: {trace.get("status")}')
        print(f'  Sender: {trace.get("sender_name")} ({trace.get("sender_phone")})')
        msg = trace.get("message") or trace.get("message_content") or "N/A"
        if isinstance(msg, str) and len(msg) > 60:
            print(f'  Message: {msg[:60]}...')
        else:
            print(f'  Message: {msg}')
        print(f'  Agent Processing: {trace.get("agent_processing_ms")}ms')
        print(f'  Evolution Success: {trace.get("evolution_success")}')
        
        if trace.get("evolution_success"):
            print("\n✅ Message successfully sent to Pavan!")
        else:
            print("\n⚠️ Evolution API may not have sent message yet")
