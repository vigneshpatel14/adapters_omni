#!/usr/bin/env python3
"""Test the new Leo agent configuration"""

import sys
sys.path.insert(0, '/c/Automagic_Omni')

from src.services.leo_agent_client import LeoAgentClient
from src.config import config

print("=" * 60)
print("Testing Leo Agent Configuration")
print("=" * 60)

print(f"\n✓ Leo API Base URL: {config.leo_agent.api_base_url}")
print(f"✓ Leo Workflow ID: {config.leo_agent.workflow_id}")
print(f"✓ Leo Bearer Token: {'✓ Set' if config.leo_agent.bearer_token else '✗ Not set'}")
print(f"✓ Leo Subscription Key: {'✓ Set' if config.leo_agent.subscription_key else '✗ Not set'}")
print(f"✓ Leo BPC: {config.leo_agent.bpc}")
print(f"✓ Leo Environment: {config.leo_agent.environment}")
print(f"✓ Leo Version: {config.leo_agent.version}")

if config.leo_agent.is_configured:
    print("\n✅ Leo Agent is CONFIGURED and ready to use")
    
    # Create a Leo client
    leo_client = LeoAgentClient(
        api_base_url=config.leo_agent.api_base_url,
        workflow_id=config.leo_agent.workflow_id,
        bearer_token=config.leo_agent.bearer_token,
        subscription_key=config.leo_agent.subscription_key,
        bpc=config.leo_agent.bpc,
        environment=config.leo_agent.environment,
        version=config.leo_agent.version
    )
    print(f"✅ Leo Agent Client created successfully")
else:
    print("\n❌ Leo Agent is NOT configured")

print("\n" + "=" * 60)
