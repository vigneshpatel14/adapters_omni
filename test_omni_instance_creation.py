#!/usr/bin/env python3
"""
Test Omni → Evolution API integration
Creates an instance in Omni pointing to your existing Evolution instance
"""

import requests
import json

# Your configuration
OMNI_API_URL = "http://localhost:8882"
OMNI_API_KEY = "omni-dev-key-test-2025"

EVOLUTION_API_URL = "https://evolution-api-production-7611.up.railway.app"
EVOLUTION_API_KEY = "VigneshKey17"  # Global API Key from Evolution Manager
EVOLUTION_INSTANCE_ID = "8b167ecf-b1a6-4165-bb0c-c2c7fbaf103e"

class OmniInstanceTester:
    def __init__(self, omni_url: str, omni_key: str):
        self.omni_url = omni_url.rstrip('/')
        self.omni_key = omni_key
        self.session = requests.Session()

    def create_instance(self, name: str, evolution_url: str, evolution_key: str, 
                       instance_id: str, agent_url: str, agent_key: str) -> Dict[str, Any]:
        """Create a WhatsApp instance in Omni pointing to Evolution API."""
        print("\n" + "="*70)
        print("CREATING OMNI INSTANCE")
        print("="*70)
        
        url = f"{self.omni_url}/api/v1/instances"
        headers = {
            "x-api-key": self.omni_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": name,
            "channel_type": "whatsapp",
            "evolution_url": evolution_url,
            "evolution_key": evolution_key,
            "whatsapp_instance": instance_id,
            "agent_api_url": agent_url,
            "agent_api_key": agent_key,
            "default_agent": "echo",
            "agent_timeout": 60
        }
        
        print(f"URL: {url}")
        print(f"Headers: {{'x-api-key': '{self.omni_key}'}}")
        print(f"Payload:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response:")
            print(json.dumps(response.json(), indent=2))
            
            if response.status_code in [200, 201]:
                print("\n✅ Instance created successfully!")
                return response.json()
            else:
                print(f"\n❌ Failed to create instance")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def list_instances(self) -> Dict[str, Any]:
        """List all instances in Omni."""
        print("\n" + "="*70)
        print("LISTING OMNI INSTANCES")
        print("="*70)
        
        url = f"{self.omni_url}/api/v1/instances"
        headers = {"x-api-key": self.omni_key}
        
        print(f"URL: {url}")
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response:")
            print(json.dumps(response.json(), indent=2))
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def get_instance(self, instance_name: str) -> Dict[str, Any]:
        """Get specific instance details."""
        print("\n" + "="*70)
        print(f"GETTING INSTANCE: {instance_name}")
        print("="*70)
        
        url = f"{self.omni_url}/api/v1/instances/{instance_name}"
        headers = {"x-api-key": self.omni_key}
        
        print(f"URL: {url}")
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response:")
            print(json.dumps(response.json(), indent=2))
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

if __name__ == "__main__":
    print("🔗 OMNI ↔ EVOLUTION API INTEGRATION TEST")
    print("="*70)
    
    tester = OmniInstanceTester(OMNI_API_URL, OMNI_API_KEY)
    
    # List existing instances
    tester.list_instances()
    
    # Create new instance pointing to your Evolution API
    instance = tester.create_instance(
        name="whatsapp-test",
        evolution_url=EVOLUTION_API_URL,
        evolution_key=EVOLUTION_API_KEY,
        instance_id=EVOLUTION_INSTANCE_ID,
        agent_url="http://localhost:8886",
        agent_key="echo-agent-key"
    )
    
    if instance:
        instance_name = instance.get("name") or instance.get("id")
        print(f"\nGetting created instance: {instance_name}")
        tester.get_instance(instance_name)
