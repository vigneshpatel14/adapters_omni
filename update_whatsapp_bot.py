#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:8882/api/v1/instances'
headers = {'x-api-key': 'omni-dev-key-test-2025'}

# Get instances
resp = requests.get(url, headers=headers, timeout=5)
instances = resp.json()

# Find whatsapp-bot instance
whatsapp_bot = next((i for i in instances if i.get('name') == 'whatsapp-bot'), None)

if whatsapp_bot:
    instance_name = whatsapp_bot['name']
    
    # Prepare update data with only the fields that can be updated
    update_data = {
        'agent_api_url': 'http://localhost:8886',  # Use localhost, not internal IP
        'whatsapp_instance': 'whatsapp-bot'  # Set the correct WhatsApp instance name
    }
    
    # PUT updated instance
    update_url = f'http://localhost:8882/api/v1/instances/{instance_name}'
    resp = requests.put(update_url, json=update_data, headers=headers, timeout=10)
    
    print(f"Updated whatsapp-bot (name: {instance_name})")
    print(f"Status: {resp.status_code}")
    print(f"Agent API URL: http://localhost:8886")
    print(f"WhatsApp Instance: whatsapp-bot")
    
    if resp.status_code != 200:
        print(f"Response: {resp.text}")
else:
    print("whatsapp-bot instance not found!")
