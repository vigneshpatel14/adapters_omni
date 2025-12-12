import requests
import json

# Get latest trace
traces_url = 'http://localhost:8882/api/v1/traces'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

response = requests.get(traces_url, headers=headers)
traces = response.json()

if traces:
    latest = traces[0]
    trace_id = latest.get('trace_id')
    
    print(f'Latest Trace ID: {trace_id}')
    print(f'Status: {latest.get("status")}')
    print(f'Sender Phone: {latest.get("sender_phone")}')
    print(f'Message Type: {latest.get("message_type")}')
    print(f'Error: {latest.get("error_message")}')
    
    # Get full trace details
    if trace_id:
        url = f'http://localhost:8882/api/v1/traces/{trace_id}'
        response = requests.get(url, headers=headers)
        trace = response.json()
        
        print(f'\nFull Trace Status: {trace.get("status")}')
        print(f'Sender Phone: {trace.get("sender_phone")}')
        print(f'Message Type: {trace.get("message_type")}')
        print(f'Agent Session ID: {trace.get("agent_session_id")}')
        print(f'Agent Processing Time: {trace.get("agent_processing_time_ms")}ms')
        print(f'Error: {trace.get("error_message")}')
        print(f'Error Stage: {trace.get("error_stage")}')
