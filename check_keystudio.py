#!/usr/bin/env python
"""Check KeyStudio_Knowledge bot instance status"""

from src.db.database import SessionLocal
from src.db.models import InstanceConfig

db = SessionLocal()

# Check if KeyStudio_Knowledge instance exists
instance = db.query(InstanceConfig).filter(
    InstanceConfig.name == "KeyStudio_Knowledge"
).first()

if instance:
    print("✅ Instance Found!")
    print(f"   Name: {instance.name}")
    print(f"   Channel Type: {instance.channel_type}")
    print(f"   Is Active: {instance.is_active}")
    print(f"   Discord Token Set: {'Yes' if instance.discord_bot_token else 'No'}")
    print(f"   Agent API URL: {instance.agent_api_url}")
    print(f"   Default Agent: {instance.default_agent}")
else:
    print("❌ Instance NOT found in database!")
    print("\nAvailable instances:")
    instances = db.query(InstanceConfig).filter(
        InstanceConfig.channel_type == "discord"
    ).all()
    for inst in instances:
        print(f"  - {inst.name} (Active: {inst.is_active})")

db.close()
