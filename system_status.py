#!/usr/bin/env python
"""Check Omni and Evolution API status"""
import requests
import json

print("=" * 70)
print("System Status Check")
print("=" * 70)

# Check Omni
print("\n1️⃣  Checking Omni API...")
url = 'http://localhost:8882/api/v1/instances'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

resp = requests.get(url, headers=headers)
print(f"   Status: {resp.status_code}")

if resp.status_code == 200:
    instances = resp.json()
    print(f"   ✅ Found {len(instances)} instance(s)")
    if instances:
        inst = instances[0]
        print(f"\n   Instance: {inst.get('name')}")
        print(f"   Is Active: {inst.get('is_active')}")
        print(f"   Agent API URL: {inst.get('agent_api_url')}")
else:
    print(f"   ❌ Error")

# Check Evolution API
print("\n2️⃣  Checking Evolution API...")
evolution_url = 'https://evolution-api-production-7611.up.railway.app'
api_key = '88B2F8C2-5098-455A-AA70-BA84B33FA492'
headers = {'apikey': api_key}

url = f'{evolution_url}/instance/fetchInstances'
resp = requests.get(url, headers=headers)
print(f"   Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    if isinstance(data, list):
        print(f"   ✅ Found {len(data)} instance(s)")
    else:
        print(f"   Response format: {type(data)}")
elif resp.status_code == 401:
    print(f"   ❌ 401 Unauthorized - API Key invalid or expired")
    print(f"\n   This is the problem!")
    print(f"   Evolution API is rejecting requests with status 401")
    print(f"   \n   Possible solutions:")
    print(f"   1. Check if the Evolution API key is correct")
    print(f"   2. Check if Evolution API service is running properly")
    print(f"   3. Try using the Evolution API Manager web interface directly")
else:
    print(f"   ❌ Error: {resp.status_code}")

print("\n" + "=" * 70)
