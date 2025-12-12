#!/usr/bin/env python3
"""
Test webhook reception and message routing.
Sends test messages to Omni API and verifies they're processed.
"""

import requests
import json
import time
from datetime import datetime

OMNI_API_URL = "http://localhost:8882"
OMNI_API_KEY = "omni-dev-key-test-2025"
INSTANCE_NAME = "whatsapp-test"

class WebhookTester:
    def __init__(self, omni_url: str, api_key: str, instance_name: str):
        self.omni_url = omni_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.session = requests.Session()

    def send_webhook(self, message_text: str, phone: str = "+1234567890") -> Dict[str, Any]:
        """Send a test webhook message to Omni."""
        print("\n" + "="*70)
        print("SENDING TEST WEBHOOK")
        print("="*70)
        
        url = f"{self.omni_url}/webhook/evolution/{self.instance_name}"
        
        # Correct Evolution API webhook format - key should be at data level, not inside message
        payload = {
            "key": {
                "id": f"msg-{int(time.time())}@c.us",
                "fromMe": False,
                "remoteJid": f"{phone}@s.whatsapp.net",
                "participant": None
            },
            "messageTimestamp": int(time.time()),
            "pushName": "Test User",
            "status": "ACK",
            "message": {
                "conversation": message_text
            },
            "sidecar": None,
            "data": {}
        }
        
        print(f"URL: {url}")
        print(f"Phone: {phone}")
        print(f"Message: {message_text}")
        print(f"Payload:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code in [200, 201]:
                print("✅ Webhook accepted")
                return {"success": True, "response": response.json()}
            else:
                print(f"❌ Webhook rejected with status {response.status_code}")
                return {"success": False, "response": response.text}
                
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")
            return {"success": False, "error": str(e)}

    def get_traces(self, limit: int = 10) -> Dict[str, Any]:
        """Retrieve message traces."""
        print("\n" + "="*70)
        print("RETRIEVING MESSAGE TRACES")
        print("="*70)
        
        url = f"{self.omni_url}/api/v1/traces"
        headers = {"x-api-key": self.api_key}
        params = {
            "instance_name": self.instance_name,
            "page": 1,
            "page_size": limit
        }
        
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                traces = data if isinstance(data, list) else data.get("traces", [])
                print(f"Found {len(traces)} traces")
                
                for i, trace in enumerate(traces[:3], 1):
                    print(f"\n--- Trace {i} ---")
                    print(f"Trace ID: {trace.get('trace_id', trace.get('id', 'N/A'))}")
                    print(f"Status: {trace.get('status', 'N/A')}")
                    print(f"User: {trace.get('source_user_id', 'N/A')}")
                    print(f"Created: {trace.get('created_at', 'N/A')}")
                    
                    # Check payloads
                    if trace.get('incoming_payload'):
                        print(f"Incoming: ✅")
                    if trace.get('agent_request_payload'):
                        print(f"Agent Request: ✅")
                    if trace.get('agent_response_payload'):
                        print(f"Agent Response: ✅")
                    if trace.get('outgoing_payload'):
                        print(f"Outgoing: ✅")
                
                print(f"\nTotal traces: {len(traces)}")
                return {"success": True, "traces": traces}
            else:
                print(f"❌ Failed to get traces")
                print(f"Response: {response.text[:500]}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Error getting traces: {e}")
            return {"success": False, "error": str(e)}

    def get_trace_detail(self, trace_id: str) -> Dict[str, Any]:
        """Get detailed trace information."""
        print("\n" + "="*70)
        print(f"TRACE DETAIL: {trace_id}")
        print("="*70)
        
        url = f"{self.omni_url}/api/v1/traces/{trace_id}"
        headers = {"x-api-key": self.api_key}
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                trace = response.json()
                print(json.dumps(trace, indent=2, default=str))
                return {"success": True, "trace": trace}
            else:
                print(f"❌ Failed to get trace")
                print(f"Response: {response.text[:500]}")
                return {"success": False}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False}

    def run_full_test(self):
        """Run complete webhook → agent → trace test."""
        print("\n" + "TEST FULL WEBHOOK → AGENT → TRACE SUITE")
        print("="*70)
        print(f"Instance: {self.instance_name}")
        print(f"Omni API: {self.omni_url}")
        
        # Test 1: Simple text message
        print("\n\n[TEST 1] Sending simple text message...")
        result = self.send_webhook("Hello Omni! This is a test message.")
        
        if result["success"]:
            print("✅ Message sent to Omni")
            
            # Wait a bit for processing
            print("\nWaiting for message processing...")
            time.sleep(2)
            
            # Test 2: Get traces
            print("\n\n[TEST 2] Retrieving traces...")
            traces_result = self.get_traces()
            
            if traces_result["success"] and traces_result.get("traces"):
                trace = traces_result["traces"][0]
                print("\n\n[TEST 3] Getting trace details...")
                self.get_trace_detail(trace.get("trace_id") or trace.get("id"))
            
        # Test 3: Send another message
        print("\n\n[TEST 4] Sending another message...")
        self.send_webhook("Second test message with more content")
        
        print("\n\n" + "="*70)
        print("✅ WEBHOOK TEST COMPLETE")
        print("="*70)
        print("""
Next Steps:
1. Check Omni API logs for message processing
2. Check echo agent logs for received requests  
3. View traces at: http://localhost:8882/api/v1/traces
4. Send real WhatsApp message to test full flow
        """)

if __name__ == "__main__":
    tester = WebhookTester(OMNI_API_URL, OMNI_API_KEY, INSTANCE_NAME)
    tester.run_full_test()
