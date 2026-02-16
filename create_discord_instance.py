#!/usr/bin/env python
"""Create a new Discord bot instance"""

import os
import sys
from src.db.database import SessionLocal
from src.db.models import InstanceConfig

def create_discord_instance():
    """Create a new Discord bot instance"""
    
    db = SessionLocal()
    
    try:
        # Get Discord token from environment
        discord_token = os.getenv('DISCORD_BOT_TOKEN')
        if not discord_token:
            print("❌ Error: DISCORD_BOT_TOKEN not found in .env")
            return False
        
        # Create new instance
        new_instance = InstanceConfig(
            name="new_discord_bot",
            channel_type="discord",
            is_active=True,
            discord_bot_token=discord_token,
            agent_api_url=os.getenv('LEO_API_BASE_URL'),
            agent_api_key=os.getenv('LEO_BEARER_TOKEN'),
            default_agent="leo",
            agent_instance_type="leo",
            agent_type="agent",
            agent_timeout=60,
        )
        
        # Check if instance already exists
        existing = db.query(InstanceConfig).filter(
            InstanceConfig.name == "new_discord_bot"
        ).first()
        
        if existing:
            print("⚠️  Instance 'new_discord_bot' already exists, updating...")
            existing.is_active = True
            existing.discord_bot_token = discord_token
            existing.agent_api_url = os.getenv('LEO_API_BASE_URL')
            existing.agent_api_key = os.getenv('LEO_BEARER_TOKEN')
            db.commit()
            print("✅ Instance updated successfully")
            return True
        
        # Add to database
        db.add(new_instance)
        db.commit()
        
        print("✅ New Discord instance created successfully!")
        print(f"   Instance: new_discord_bot")
        print(f"   Channel: discord")
        print(f"   Agent: leo")
        print(f"   Status: active")
        print(f"   ID: {new_instance.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating instance: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_discord_instance()
    sys.exit(0 if success else 1)
