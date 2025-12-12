import requests
import json

# Get the full trace details
trace_id = 'd8bf6d3a-1bba-43a1-8d7a-ffeb6b8ba691'
traces_url = f'http://localhost:8882/api/v1/traces/{trace_id}'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

try:
    response = requests.get(traces_url, headers=headers)
    trace = response.json()
    
    print('=' * 60)
    print('FULL TRACE DETAILS')
    print('=' * 60)
    print(json.dumps(trace, indent=2, default=str))
except Exception as e:
    print(f'Error: {e}')
