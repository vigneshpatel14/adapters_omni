import requests
import json
from datetime import datetime
import time

# Create a test message that we can trace
print("=" * 70)
print("SENDING TEST MESSAGE TO TRACE THE SEND REQUEST")
print("=" * 70)

webhook_payload = {
    'event': 'messages.upsert',
    'data': {
        'messages': [
            {
                'key': {
                    'remoteJid': '917396804318@s.whatsapp.net',
                    'fromMe': False,
                    'id': f'trace_test_{int(time.time())}'
                },
                'message': {
                    'conversation': 'Trace test message to check Evolution send'
                },
                'messageTimestamp': int(datetime.now().timestamp()),
                'pushName': 'Balaji',
                'status': 'PENDING'
            }
        ]
    }
}

webhook_url = 'http://localhost:8882/webhook/evolution/whatsapp-test'
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(webhook_url, json=webhook_payload, headers=headers, timeout=10)
    trace_id = response.json().get('trace_id')
    print(f"✅ Webhook sent, Trace ID: {trace_id}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Wait for processing
time.sleep(3)

# Check the logs to see what requests were made
print("\n" + "=" * 70)
print("CHECKING LOGS FOR EVOLUTION API REQUESTS")
print("=" * 70)

# Read the latest log file
import os
log_dir = './logs'
log_files = [f for f in os.listdir(log_dir) if f.startswith('omnihub_')]
log_files.sort()

if log_files:
    latest_log = log_files[-1]
    log_path = os.path.join(log_dir, latest_log)
    
    print(f"\nReading: {latest_log}")
    print("\nSearching for Evolution API send requests...")
    
    with open(log_path, 'r') as f:
        lines = f.readlines()
    
    # Look for recent Evolution API requests
    evolution_lines = [l for l in lines if 'evolution_api_sender' in l.lower() or 'sendtext' in l.lower()]
    
    if evolution_lines:
        print(f"\n✅ Found {len(evolution_lines)} Evolution API related logs:")
        for line in evolution_lines[-20:]:  # Last 20 lines
            print(line.rstrip())
    else:
        print("⚠️  No Evolution API send logs found")
        
        # Show any errors
        error_lines = [l for l in lines if 'error' in l.lower()]
        if error_lines:
            print(f"\n⚠️  Found {len(error_lines)} error logs:")
            for line in error_lines[-10:]:
                print(line.rstrip())
