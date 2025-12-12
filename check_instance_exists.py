#!/usr/bin/env python
"""Check if whatsapp-test instance exists in Evolution API"""
import requests
import json

evolution_url = 'https://evolution-api-production-7611.up.railway.app'
api_key = '88B2F8C2-5098-455A-AA70-BA84B33FA492'

headers = {'apikey': api_key}

# List instances
url = f'{evolution_url}/instance/fetchInstances'
resp = requests.get(url, headers=headers)

if resp.status_code == 200:
    data = resp.json()
    if isinstance(data, list):
        print(f'Found {len(data)} instance(s) in Evolution API:')
        for inst in data:
            print(f'  - {inst.get("name")} (connectionStatus: {inst.get("connectionStatus")})')
        
        # Check for whatsapp-test
        found = any(inst.get("name") == "whatsapp-test" for inst in data)
        if found:
            print(f'\n✅ whatsapp-test instance EXISTS in Evolution API')
        else:
            print(f'\n❌ whatsapp-test instance DOES NOT exist in Evolution API')
            print(f'   Need to recreate it')
    else:
        print('Unexpected response format')
else:
    print(f'Error: {resp.status_code}')
