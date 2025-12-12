#!/usr/bin/env python3
"""
Discover Evolution API endpoints and test instance creation.
"""

import requests
import json
from typing import Dict, Any

EVOLUTION_API_URL = "https://evolution-api-production-7611.up.railway.app"
GLOBAL_API_KEY = "VigneshKey17"

class EvolutionAPIDiscovery:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()

    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint."""
        url = f"{self.base_url}{endpoint}"
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": response.status_code,
                "success": response.status_code in [200, 201, 204],
                "response": response.text[:500]
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status": "ERROR",
                "success": False,
                "response": str(e)[:500]
            }

    def discover_endpoints(self):
        """Test common Evolution API endpoints."""
        print("\n" + "="*70)
        print("DISCOVERING EVOLUTION API ENDPOINTS")
        print("="*70)
        
        endpoints_to_test = [
            # Root/Health
            ("/", "GET"),
            ("/api", "GET"),
            ("/status", "GET"),
            ("/info", "GET"),
            
            # Instance Management (v1 style)
            ("/api/instances", "GET"),
            ("/api/v1/instances", "GET"),
            
            # Instance Management (v2 style)
            ("/instances", "GET"),
            ("/api/instance", "GET"),
            
            # Manager endpoints
            ("/manager", "GET"),
            ("/manager/instances", "GET"),
            ("/api/manager/instances", "GET"),
            
            # Legacy endpoints
            ("/instance/list", "GET"),
            ("/instance", "GET"),
        ]
        
        results = []
        for endpoint, method in endpoints_to_test:
            result = self.test_endpoint(endpoint, method)
            results.append(result)
            
            status_symbol = "✅" if result["success"] else "❌"
            print(f"{status_symbol} {method:6} {endpoint:50} [{result['status']}]")
            if result["success"]:
                print(f"   Response: {result['response'][:100]}...")
        
        print("\n" + "="*70)
        print("SUCCESSFUL ENDPOINTS")
        print("="*70)
        
        successful = [r for r in results if r["success"]]
        if successful:
            for r in successful:
                print(f"✅ {r['method']:6} {r['endpoint']}")
                print(f"   Response: {r['response'][:200]}")
        else:
            print("No successful endpoints found!")
        
        return results, successful

    def create_instance(self, instance_name: str, phone: str = None) -> Dict[str, Any]:
        """Try to create a new instance."""
        print("\n" + "="*70)
        print(f"ATTEMPTING TO CREATE INSTANCE: {instance_name}")
        print("="*70)
        
        # Try different creation endpoints
        creation_attempts = [
            {
                "endpoint": "/api/instances",
                "method": "POST",
                "data": {
                    "name": instance_name,
                    "integration": "WHATSAPP-BAILEYS",
                    "phone": phone
                }
            },
            {
                "endpoint": "/api/v1/instances",
                "method": "POST",
                "data": {
                    "name": instance_name,
                    "integration": "WHATSAPP-BAILEYS",
                    "phone": phone
                }
            },
            {
                "endpoint": "/instances",
                "method": "POST",
                "data": {
                    "name": instance_name,
                    "integration": "WHATSAPP-BAILEYS",
                    "phone": phone
                }
            },
            {
                "endpoint": "/instance",
                "method": "POST",
                "data": {
                    "name": instance_name,
                    "integration": "WHATSAPP-BAILEYS",
                    "phone": phone
                }
            },
        ]
        
        for attempt in creation_attempts:
            print(f"\nTrying: {attempt['method']} {attempt['endpoint']}")
            print(f"Payload: {json.dumps(attempt['data'], indent=2)}")
            
            result = self.test_endpoint(
                attempt['endpoint'],
                attempt['method'],
                attempt['data']
            )
            
            print(f"Status: {result['status']}")
            print(f"Response: {result['response']}")
            
            if result['success']:
                print("✅ Creation successful!")
                return result
        
        print("❌ No successful creation endpoints found")
        return None

if __name__ == "__main__":
    discovery = EvolutionAPIDiscovery(EVOLUTION_API_URL, GLOBAL_API_KEY)
    
    print(f"\n🔍 Evolution API Discovery Tool")
    print(f"URL: {EVOLUTION_API_URL}")
    print(f"API Key: {GLOBAL_API_KEY}")
    
    # Discover endpoints
    all_results, successful = discovery.discover_endpoints()
    
    # Try to create an instance
    discovery.create_instance("omni-test-instance")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("""
1. Review the successful endpoints above
2. Use those endpoints in the Omni instance configuration
3. If instance creation worked, use the returned instance ID
4. If not, manually create via Evolution Manager and get the instance ID
    """)
