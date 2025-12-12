#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:8882/api/v1/traces'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

resp = requests.get(url, headers=headers)
traces = resp.json()

if isinstance(traces, list) and len(traces) > 0:
    # Get most recent trace
    trace = traces[-1]
    print('=== MOST RECENT TRACE ===')
    print(f'Trace ID: {trace.get("id")}')
    print(f'Status: {trace.get("status")}')
    print(f'Channel: {trace.get("channel")}')
    print(f'Sender: {trace.get("sender_phone")}')
    print(f'Message: {trace.get("message_content")}')
    print(f'Created: {trace.get("created_at")}')
    print(f'\nAgent Response: {trace.get("agent_response")}')
    print(f'Agent Status: {trace.get("agent_status")}')
    print(f'Evolution Send Status: {trace.get("evolution_send_status")}')
    print(f'Error: {trace.get("error")}')
    print(f'\n=== FULL TRACE ===')
    print(json.dumps(trace, indent=2, default=str))
else:
    print('No traces found or error:', traces)
