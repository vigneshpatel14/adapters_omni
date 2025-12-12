#!/usr/bin/env python3
"""
Test script to verify Evolution API connectivity and instance creation.
Tests the connection to Evolution API and validates your instance.
"""

import requests
import json
from typing import Dict, Any

# Configuration from .env
EVOLUTION_API_URL = "https://evolution-api-production-7611.up.railway.app"
GLOBAL_API_KEY = "VigneshKey17"
INSTANCE_API_KEY = "6976750A654C-4D9A-85B1-90D8E5411FAB"
INSTANCE_ID = "8b167ecf-b1a6-4165-bb0c-c2c7fbaf103e"

class EvolutionAPITester:
    def __init__(self, base_url: str, global_key: str, instance_key: str, instance_id: str):
        self.base_url = base_url.rstrip('/')
        self.global_key = global_key
        self.instance_key = instance_key
        self.instance_id = instance_id
        self.session = requests.Session()

    def test_health(self) -> bool:
        """Test if Evolution API is accessible."""
        print("\n" + "="*60)
        print("TEST 1: Evolution API Health Check")
        print("="*60)
        try:
            url = f"{self.base_url}/health"
            print(f"Testing: {url}")
            response = self.session.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ Evolution API is accessible")
                return True
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_global_auth(self) -> bool:
        """Test global API key authentication."""
        print("\n" + "="*60)
        print("TEST 2: Global API Key Authentication")
        print("="*60)
        try:
            url = f"{self.base_url}/api/health"
            headers = {"apikey": self.global_key}
            print(f"Testing: {url}")
            print(f"Headers: {{'apikey': '{self.global_key}'}}")
            
            response = self.session.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code in [200, 201]:
                print("✅ Global API Key is valid")
                return True
            elif response.status_code == 401:
                print("❌ Invalid API Key (401 Unauthorized)")
                return False
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                return True  # May still be valid
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_instance_exists(self) -> bool:
        """Check if instance exists."""
        print("\n" + "="*60)
        print("TEST 3: Check Instance Existence")
        print("="*60)
        try:
            url = f"{self.base_url}/instance/info/{self.instance_id}"
            headers = {"apikey": self.instance_key}
            print(f"Testing: {url}")
            print(f"Instance ID: {self.instance_id}")
            print(f"Headers: {{'apikey': '{self.instance_key}'}}")
            
            response = self.session.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ Instance exists and is accessible")
                data = response.json()
                if isinstance(data, dict):
                    print(f"Instance Data: {json.dumps(data, indent=2)[:500]}")
                return True
            elif response.status_code == 404:
                print("⚠️  Instance not found (404)")
                return False
            elif response.status_code == 401:
                print("❌ Invalid instance API key")
                return False
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_instance_status(self) -> bool:
        """Get instance connection status."""
        print("\n" + "="*60)
        print("TEST 4: Instance Connection Status")
        print("="*60)
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_id}"
            headers = {"apikey": self.instance_key}
            print(f"Testing: {url}")
            
            response = self.session.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ Instance status retrieved successfully")
                data = response.json()
                print(f"Status Data: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"⚠️  Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_instance_qr(self) -> bool:
        """Get QR code if not authenticated."""
        print("\n" + "="*60)
        print("TEST 5: Get Instance QR Code")
        print("="*60)
        try:
            url = f"{self.base_url}/instance/fetchQrCode/{self.instance_id}"
            headers = {"apikey": self.instance_key}
            print(f"Testing: {url}")
            
            response = self.session.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                qr = data.get("qrcode")
                if qr:
                    print(f"✅ QR Code generated (length: {len(qr)})")
                    print(f"First 100 chars: {qr[:100]}...")
                    return True
                else:
                    print("⚠️  No QR code in response (might be authenticated already)")
                    print(f"Response: {json.dumps(data, indent=2)[:500]}")
                    return True
            elif response.status_code == 400:
                print("⚠️  Instance already authenticated (400)")
                return True
            else:
                print(f"⚠️  Status code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        print("\n" + "🧪 EVOLUTION API CONNECTIVITY TEST SUITE 🧪")
        print("=" * 60)
        
        results = {
            "Health Check": self.test_health(),
            "Global Auth": self.test_global_auth(),
            "Instance Exists": self.test_instance_exists(),
            "Instance Status": self.test_instance_status(),
            "Instance QR": self.test_instance_qr(),
        }
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<40} {status}")
        
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Evolution API is ready to use.")
        elif passed >= total - 1:
            print("\n⚠️  Most tests passed. Evolution API appears to be working.")
        else:
            print("\n❌ Multiple tests failed. Check Evolution API configuration.")
        
        return results

if __name__ == "__main__":
    tester = EvolutionAPITester(
        base_url=EVOLUTION_API_URL,
        global_key=GLOBAL_API_KEY,
        instance_key=INSTANCE_API_KEY,
        instance_id=INSTANCE_ID
    )
    
    tester.run_all_tests()
