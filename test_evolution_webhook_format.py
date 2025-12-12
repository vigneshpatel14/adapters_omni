#!/usr/bin/env python3
"""
Test webhook with real Evolution API format
"""
import requests
import json
import time

OMNI_API_URL = "http://localhost:8882"
INSTANCE_NAME = "whatsapp-test"

def send_webhook_message(message_text, phone="+918853074521"):
    """Send a test webhook message with correct Evolution API format"""
    print("\n" + "="*70)
    print("SENDING WEBHOOK WITH EVOLUTION API FORMAT")
    print("="*70)
    
    url = f"{OMNI_API_URL}/webhook/evolution/{INSTANCE_NAME}"
    
    # Correct Evolution API webhook format from sample_data.py
    payload = {
        "event": "messages.upsert",
        "data": {
            "messages": [
                {
                    "key": {
                        "remoteJid": f"{phone}@s.whatsapp.net",
                        "id": f"msg_{int(time.time())}@c.us",
                        "fromMe": False,
                    },
                    "message": {"conversation": message_text},
                    "messageTimestamp": int(time.time()),
                    "pushName": "Test User",
                    "status": "received",
                }
            ]
        },
        "instance": INSTANCE_NAME,
    }
    
    print(f"\nURL: {url}")
    print(f"Phone: {phone}")
    print(f"Message: {message_text}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Webhook accepted")
            return response.json()
        else:
            print(f"❌ Webhook rejected")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_traces():
    """Get message traces"""
    print("\n" + "="*70)
    print("GETTING MESSAGE TRACES")
    print("="*70)
    
    url = f"{OMNI_API_URL}/api/v1/traces"
    params = {
        "instance_name": INSTANCE_NAME,
        "page": 1,
        "page_size": 10
    }
    headers = {"x-api-key": "omni-dev-key-test-2025"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            traces = response.json()
            print(f"\nTraces ({len(traces)}):")
            for i, trace in enumerate(traces[:3], 1):
                print(f"\n[Trace {i}]")
                print(f"  ID: {trace.get('trace_id')}")
                print(f"  Status: {trace.get('status')}")
                print(f"  Sender: {trace.get('sender_phone')} ({trace.get('sender_name')})")
                print(f"  Message Type: {trace.get('message_type')}")
                print(f"  Message ID: {trace.get('whatsapp_message_id')}")
                
                if trace.get('trace_id'):
                    get_trace_detail(trace['trace_id'])
            
            return traces
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_trace_detail(trace_id):
    """Get detailed trace information"""
    url = f"{OMNI_API_URL}/api/v1/traces/{trace_id}"
    headers = {"x-api-key": "omni-dev-key-test-2025"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            trace = response.json()
            print(f"  Detailed Status: {trace.get('status')}")
            if trace.get('error_message'):
                print(f"  Error: {trace.get('error_message')} (stage: {trace.get('error_stage')})")
            if trace.get('agent_processing_time_ms'):
                print(f"  Agent Processing: {trace['agent_processing_time_ms']}ms")
    except:
        pass

def main():
    print("\n" + "🤖 "*20)
    print("TESTING EVOLUTION API WEBHOOK FORMAT")
    print("🤖 "*20)
    
    # Send test messages
    messages = [
        "Hello! Can you echo this back?",
        "This is a test message from WhatsApp bot"
    ]
    
    for msg in messages:
        result = send_webhook_message(msg)
        time.sleep(1)
    
    # Get traces
    time.sleep(2)
    get_traces()

if __name__ == "__main__":
    main()
