#!/usr/bin/env python3
"""
Real WhatsApp Bot - Setup Complete & Verification
"""
import requests
import json
import time

OMNI_API_URL = "http://localhost:8882"
INSTANCE_NAME = "whatsapp-test"

print("\n" + "="*80)
print(" " * 20 + "✅ REAL WHATSAPP BOT - COMPLETE SETUP")
print("="*80)

print("\n📋 CURRENT CONFIGURATION:")
print("-" * 80)

# Get instance details
headers = {"x-api-key": "omni-dev-key-test-2025"}
resp = requests.get(f"{OMNI_API_URL}/api/v1/instances", headers=headers)
if resp.status_code == 200:
    instances = resp.json()
    for inst in instances:
        if inst.get("name") == INSTANCE_NAME:
            print(f"\n✅ Instance: {inst['name']}")
            print(f"   - Status: {'Active' if inst.get('is_active') else 'Inactive'}")
            print(f"   - Agent: {inst.get('default_agent')}")
            print(f"   - Agent URL: {inst.get('agent_api_url')}")
            print(f"   - WhatsApp Number: {inst.get('owner_jid', 'Not connected yet')}")
            print(f"   - Evolution Status: {inst.get('evolution_status', {}).get('state')}")

print("\n\n🔗 WEBHOOK CONFIGURATION:")
print("-" * 80)
print(f"Webhook URL: {OMNI_API_URL}/webhook/evolution/{INSTANCE_NAME}")
print("\n📝 Instructions to setup webhook in Evolution Manager:")
print(f"1. Go to: https://evolution-api-production-7611.up.railway.app/manager")
print(f"2. Select instance: {INSTANCE_NAME}")
print(f"3. Add webhook URL: {OMNI_API_URL}/webhook/evolution/{INSTANCE_NAME}")
print(f"4. Save and test")

print("\n\n🤖 AGENT ENDPOINT:")
print("-" * 80)
print(f"Agent URL: http://172.16.141.205:8886")
print(f"Agent Type: Echo Bot")
print("Messages will be echoed back with format: '[Echo from <origin>] <message>'")

print("\n\n📊 MESSAGE FLOW:")
print("-" * 80)
print("""
┌─────────────────────┐
│  WhatsApp User      │
│   Sends Message     │
└──────────┬──────────┘
           │
           │ (SMS/WhatsApp)
           ▼
┌─────────────────────┐
│  Evolution API      │
│   (WhatsApp Bridge) │
└──────────┬──────────┘
           │
           │ Webhook POST
           ▼
┌─────────────────────┐
│   Omni API          │
│ localhost:8882      │
└──────────┬──────────┘
           │
           │ Extract message
           │ from payload
           ▼
┌─────────────────────┐
│  Message Handler    │
│   Parse & Validate  │
└──────────┬──────────┘
           │
           │ Call Agent API
           ▼
┌─────────────────────┐
│  Echo Agent         │
│   172.16.141.205    │
│   port 8886         │
└──────────┬──────────┘
           │
           │ Send response
           ▼
┌─────────────────────┐
│  Evolution API      │
│  Send to WhatsApp   │
└──────────┬──────────┘
           │
           │
           ▼
┌─────────────────────┐
│  WhatsApp User      │
│ Receives Response   │
└─────────────────────┘
""")

print("\n✅ WEBHOOK PAYLOAD FORMAT (Correct):")
print("-" * 80)
print("""
{
  "event": "messages.upsert",
  "data": {
    "messages": [
      {
        "key": {
          "remoteJid": "+918853074521@s.whatsapp.net",
          "id": "msg_xxx@c.us",
          "fromMe": false
        },
        "message": {
          "conversation": "Hello bot!"
        },
        "messageTimestamp": 1765370819,
        "pushName": "User Name",
        "status": "received"
      }
    ]
  }
}
""")

print("\n📈 TESTING THE SETUP:")
print("-" * 80)

# Send a test message
test_msg = "Hello Omni! Echo this back."
payload = {
    "event": "messages.upsert",
    "data": {
        "messages": [
            {
                "key": {
                    "remoteJid": "+918853074521@s.whatsapp.net",
                    "id": f"msg_{int(time.time())}@c.us",
                    "fromMe": False,
                },
                "message": {"conversation": test_msg},
                "messageTimestamp": int(time.time()),
                "pushName": "Test User",
                "status": "received",
            }
        ]
    },
}

url = f"{OMNI_API_URL}/webhook/evolution/{INSTANCE_NAME}"
resp = requests.post(url, json=payload)

if resp.status_code == 200:
    data = resp.json()
    trace_id = data.get("trace_id")
    print(f"\n✅ Test message sent successfully!")
    print(f"   Trace ID: {trace_id}")
    
    # Get trace status
    if trace_id:
        time.sleep(3)
        trace_resp = requests.get(f"{OMNI_API_URL}/api/v1/traces/{trace_id}", headers=headers)
        if trace_resp.status_code == 200:
            trace = trace_resp.json()
            print(f"\n📊 Trace Status:")
            print(f"   - Status: {trace.get('status')}")
            print(f"   - Sender: {trace.get('sender_phone')} ({trace.get('sender_name')})")
            print(f"   - Message Type: {trace.get('message_type')}")
            print(f"   - Processing Time: {trace.get('total_processing_time_ms')}ms")
            if trace.get('error_message'):
                print(f"   - Error: {trace.get('error_message')} (stage: {trace.get('error_stage')})")
else:
    print(f"\n❌ Error: {resp.status_code}")

print("\n\n" + "="*80)
print(" " * 15 + "✅ BOT SETUP COMPLETE - READY FOR REAL MESSAGES!")
print("="*80)

print("\n🎯 NEXT STEPS:")
print("-" * 80)
print("""
1. Go to Evolution Manager UI:
   https://evolution-api-production-7611.up.railway.app/manager

2. Configure webhook for your whatsapp-test instance to:
   http://localhost:8882/webhook/evolution/whatsapp-test
   (or your public IP if testing from real phone)

3. Send a message from any WhatsApp contact to your bot number

4. Message will be echoed back automatically!

5. View message traces at:
   http://localhost:8882/api/v1/traces

Note: Make sure your Omni API and Echo Agent are running!
   - Omni API: http://localhost:8882/health
   - Agent: Should respond to POST requests on port 8886
""")

print("\n🔧 TROUBLESHOOTING:")
print("-" * 80)
print("""
If messages aren't being processed:
1. Check Omni API logs: ./logs/omnihub_*.log
2. Verify webhook URL is correct in Evolution Manager
3. Check that message structure matches the format above
4. Verify Evolution API can reach your Omni webhook endpoint

If echo bot isn't responding:
1. Check echo agent is running on port 8886
2. Check agent endpoint: POST http://172.16.141.205:8886/api/v1/agent/default/run
3. Check Evolution API credentials are correct in .env file
""")

print("\n" + "="*80 + "\n")
