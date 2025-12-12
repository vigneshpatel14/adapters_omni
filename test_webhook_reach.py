#!/usr/bin/env python
"""Test if Evolution API can reach your webhook"""
import requests
import json

print("=" * 70)
print("Testing Webhook Network Connectivity")
print("=" * 70)

# Your webhook endpoint
webhook_url = "http://172.16.141.205:8882/webhook/evolution/whatsapp-test"

print(f"\nWebhook URL: {webhook_url}")
print(f"Testing connectivity from this machine...\n")

# Test 1: Simple GET request
print("Test 1: Direct connection from Python")
try:
    resp = requests.get(webhook_url, timeout=5)
    print(f"  Status: {resp.status_code}")
    print(f"  ✅ Connection successful!")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: POST with test message
print("\nTest 2: POST with test webhook message")
test_payload = {
    "data": "eyJrZXkiOiB7InJlbW90ZUppZCI6ICI5MTkwMTQ0NTY0MjFAcy53aGF0c2FwcC5uZXQiLCAiZnJvbU1lIjogZmFsc2UsICJpZCI6ICJ0ZXN0XzEifSwgIm1lc3NhZ2VUaW1lc3RhbXAiOiAxNzY1Mzc2MDAwLCAicHVzaE5hbWUiOiAiVGVzdCBVc2VyIiwgInN0YXR1cyI6ICJQRU5ESU5HIiwgIm1lc3NhZ2UiOiB7ImNvbnZlcnNhdGlvbiI6ICJIZTFSBYIBBBJHYT4s" 
}

try:
    resp = requests.post(webhook_url, json=test_payload, timeout=5)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"  ✅ POST successful!")
    else:
        print(f"  ⚠️ POST returned {resp.status_code}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 70)
print("Network Test Result:")
print("=" * 70)

try:
    resp = requests.get(webhook_url, timeout=5)
    print(f"\n✅ Your webhook IS REACHABLE")
    print(f"\nThis means:")
    print(f"  - Network connectivity is fine")
    print(f"  - Evolution API SHOULD be able to reach your webhook")
    print(f"\nIf webhook still not being called by Evolution API:")
    print(f"  - The issue is on Evolution API's side")
    print(f"  - Or Evolution API needs time to recognize the new webhook URL")
    print(f"  - Try waiting a few minutes and sending a message again")
except Exception as e:
    print(f"\n❌ Your webhook is NOT REACHABLE")
    print(f"\nError: {e}")
    print(f"\nThis means Evolution API cannot reach your endpoint!")
    print(f"Possible causes:")
    print(f"  - Firewall blocking port 8882")
    print(f"  - Your API server is not running")
    print(f"  - Incorrect IP address: 172.16.141.205")
