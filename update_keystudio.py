#!/usr/bin/env python
"""Update keystudio-knowledge instance with correct Leo API endpoint"""

from src.db.database import SessionLocal
from src.db.models import InstanceConfig
import os

db = SessionLocal()

# Get the instance
instance = db.query(InstanceConfig).filter(
    InstanceConfig.name == 'keystudio-knowledge'
).first()

if instance:
    # Update with the new Leo API endpoint
    instance.agent_api_url = "https://api-build.gep.com/leo-portal-agentic-runtime-node-api/v1"
    
    # Get the new bearer token from environment or use default
    new_bearer_token = os.getenv('LEO_BEARER_TOKEN', '')
    if new_bearer_token:
        instance.agent_api_key = new_bearer_token
    
    db.commit()
    
    print("✅ Updated keystudio-knowledge instance!")
    print(f"   Agent API URL: {instance.agent_api_url}")
    print(f"   Agent API Key: {'Set' if instance.agent_api_key else 'Not set'}")
else:
    print("❌ Instance not found")

db.close()
