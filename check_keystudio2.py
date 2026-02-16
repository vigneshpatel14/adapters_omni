#!/usr/bin/env python
"""Check KeyStudio Knowledge bot status"""

from src.db.database import SessionLocal
from src.db.models import InstanceConfig

db = SessionLocal()
instance = db.query(InstanceConfig).filter(
    InstanceConfig.name == 'keystudio-knowledge'
).first()

if instance:
    print('✅ KeyStudio Instance Found!')
    print(f'   Name: {instance.name}')
    print(f'   Channel Type: {instance.channel_type}')
    print(f'   Is Active: {instance.is_active}')
    token_status = 'Yes' if instance.discord_bot_token else 'No'
    print(f'   Discord Token Set: {token_status}')
    print(f'   Agent API URL: {instance.agent_api_url}')
    print(f'   Default Agent: {instance.default_agent}')
else:
    print('❌ Not found')

db.close()
