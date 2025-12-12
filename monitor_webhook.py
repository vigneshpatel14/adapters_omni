#!/usr/bin/env python
"""Monitor webhook endpoint for incoming messages"""
import time
from datetime import datetime
import subprocess
import os

print("=" * 70)
print("Monitoring Webhook for Incoming Messages")
print("=" * 70)

log_file = "c:\\Automagic_Omni\\logs\\omnihub_app.log"

print(f"\nWatching log file: {log_file}")
print(f"Waiting for webhook calls...")
print("\n📌 Send a message now from WhatsApp to your bot number!")
print("=" * 70 + "\n")

# Get initial file size
if os.path.exists(log_file):
    initial_size = os.path.getsize(log_file)
else:
    initial_size = 0

# Monitor for 30 seconds
start_time = time.time()
found_webhook = False

while time.time() - start_time < 30:
    if os.path.exists(log_file):
        current_size = os.path.getsize(log_file)
        
        if current_size > initial_size:
            # New logs written
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(initial_size)
                    new_logs = f.read()
                    
                if 'WEBHOOK' in new_logs or 'webhook' in new_logs:
                    print("✅ WEBHOOK CALLED!")
                    print(f"New logs (last 500 chars):\n{new_logs[-500:]}\n")
                    found_webhook = True
                    break
                elif 'POST /webhook' in new_logs:
                    print("✅ WEBHOOK ENDPOINT HIT!")
                    print(f"New logs (last 300 chars):\n{new_logs[-300:]}\n")
                    found_webhook = True
                    break
                    
            except Exception as e:
                print(f"Error reading logs: {e}")
    
    time.sleep(1)

if not found_webhook:
    print("❌ NO WEBHOOK CALL DETECTED in last 30 seconds")
    print("\nThis means Evolution API is NOT sending messages to your webhook!")
    print("\nPossible causes:")
    print("  1. WhatsApp instance is still not properly connected")
    print("  2. Evolution API webhook URL is incorrect")
    print("  3. Network connectivity issue")
    print("\nNext steps:")
    print("  1. Check Evolution API Manager: https://evolution-api-production-7611.up.railway.app/manager")
    print("  2. Verify the instance shows 'Connected' status")
    print("  3. Check webhook URL is: http://172.16.141.205:8882/webhook/evolution/whatsapp-test")
else:
    print("✅ Webhook is working! Check the logs for message details.")
