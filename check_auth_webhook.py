#!/usr/bin/env python
"""Check instance authentication and webhook status"""
import requests
import json

instance_name = 'whatsapp-test'
evolution_url = 'https://evolution-api-production-7611.up.railway.app'
api_key = '88B2F8C2-5098-455A-AA70-BA84B33FA492'

headers = {'apikey': api_key}

# Get full instance details
url = f'{evolution_url}/instance/fetchInstances'
resp = requests.get(url, headers=headers)
data = resp.json()

print("=" * 70)
print("Instance Authentication & Webhook Status")
print("=" * 70)

if isinstance(data, list):
    for inst in data:
        if inst.get('name') == instance_name:
            print(f'\nInstance Details:')
            print(f'  Name: {inst.get("name")}')
            print(f'  Connection Status: {inst.get("connectionStatus")}')
            print(f'  Owner JID: {inst.get("ownerJid")}')
            print(f'  Updated At: {inst.get("updatedAt")}')
            print(f'  Disconnection Reason: {inst.get("disconnectionReasonCode")}')
            print(f'  Disconnection At: {inst.get("disconnectionAt")}')
            
            # Key indicators
            if inst.get('ownerJid'):
                print(f'\n✅ Instance HAS ownerJid - appears to be authenticated')
            else:
                print(f'\n❌ Instance NO ownerJid - NOT authenticated!')
                
            # Check webhook
            webhook_url = f'{evolution_url}/webhook/find/{instance_name}'
            webhook_resp = requests.get(webhook_url, headers=headers)
            webhook = webhook_resp.json()
            
            print(f'\nWebhook Configuration:')
            print(f'  Enabled: {webhook.get("enabled")}')
            print(f'  URL: {webhook.get("url")}')
            print(f'  Updated: {webhook.get("updatedAt")}')
            print(f'  Events: {webhook.get("events")}')
            
            # Summary
            print(f'\n📋 Summary:')
            if inst.get('ownerJid') and webhook.get('enabled') and webhook.get('url'):
                print(f'✅ Everything looks configured!')
                print(f'   Instance is authenticated and webhook is enabled')
                print(f'   Messages should be flowing to your webhook')
            elif not inst.get('ownerJid'):
                print(f'❌ Instance is NOT authenticated')
                print(f'   Need to: Go to Evolution Manager and scan QR code')
            elif not webhook.get('enabled'):
                print(f'❌ Webhook is disabled')
            elif not webhook.get('url'):
                print(f'❌ Webhook URL not set')
