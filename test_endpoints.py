import requests

# Try different endpoint variations
endpoints = [
    'http://localhost:8886/health',
    'http://localhost:8886/api/v1/agent/default/run',
    'http://localhost:8886/api/agent/chat',
    'http://localhost:8886/api/v1/agent/run',
    'http://localhost:8886/chat',
    'http://localhost:8886/run',
]

for endpoint in endpoints:
    try:
        response = requests.get(endpoint, timeout=2)
        print(f'{endpoint}: {response.status_code}')
    except Exception as e:
        print(f'{endpoint}: ERROR - {str(e)[:50]}')
