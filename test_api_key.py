#!/usr/bin/env python
"""Test Evolution API key"""
import requests

api_key = '88B2F8C2-5098-455A-AA70-BA84B33FA492'
evolution_url = 'https://evolution-api-production-7611.up.railway.app'

headers = {'apikey': api_key}

# Test API key
url = f'{evolution_url}/instance/fetchInstances'
resp = requests.get(url, headers=headers, timeout=10)

print(f'Evolution API Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'API Key is valid')
    print(f'Instances: {len(data) if isinstance(data, list) else "unknown"}')
    if isinstance(data, list) and data:
        for inst in data:
            print(f'  - {inst.get("name")}')
else:
    print(f'API Key rejected: {resp.status_code}')
    print(f'Response: {resp.text[:300]}')
