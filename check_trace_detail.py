#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta

# Get trace details
trace_id = "ff1ff0da-c57b-429b-a378-d4a242a4ef29"
url = f'http://localhost:8882/api/v1/traces/{trace_id}'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

resp = requests.get(url, headers=headers)
if resp.status_code == 200:
    trace = resp.json()
    print('=== TRACE DETAILS ===')
    print(json.dumps(trace, indent=2, default=str))
else:
    print(f'Status: {resp.status_code}')
    print('Response:', resp.text)

# Also get recent traces
print('\n=== ALL RECENT TRACES ===')
url = 'http://localhost:8882/api/v1/traces'
resp = requests.get(url, headers=headers)
traces = resp.json()
if isinstance(traces, list):
    for i, t in enumerate(traces[-5:]):
        print(f"\nTrace {i}: {t.get('trace_id')}")
        print(f"  Status: {t.get('status')}")
        print(f"  Sender: {t.get('sender_phone')}")
        print(f"  Message: {t.get('message_type')}")
        print(f"  Error: {t.get('error_message')}")
