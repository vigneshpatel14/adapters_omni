#!/usr/bin/env python3
"""Check what Discord instances the service manager would find."""

from src.db.database import SessionLocal
from src.db.models import InstanceConfig

db = SessionLocal()
try:
    instances = (
        db.query(InstanceConfig)
        .filter(
            InstanceConfig.channel_type == "discord",
            InstanceConfig.is_active == True,
            InstanceConfig.discord_bot_token.isnot(None),
        )
        .limit(10)
        .all()
    )

    print(f"\n=== Found {len(instances)} active Discord instances ===\n")
    for inst in instances:
        print(f"Name: {inst.name}")
        print(f"  ID: {inst.id}")
        print(f"  Token: {'***' if inst.discord_bot_token else 'None'}")
        print(f"  Voice Enabled: {inst.discord_voice_enabled}")
        print()
finally:
    db.close()
