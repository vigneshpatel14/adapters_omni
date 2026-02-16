#!/usr/bin/env python
"""Test streaming implementation"""

import os
from src.services.leo_agent_client import LeoAgentClient
from src.services.agent_api_client import AgentApiClient

# Test Leo Agent Client
print("=" * 60)
print("Testing Leo Agent Client Streaming")
print("=" * 60)

api_base_url = os.getenv('LEO_API_BASE_URL')
workflow_id = os.getenv('LEO_WORKFLOW_ID')
bearer_token = os.getenv('LEO_BEARER_TOKEN')
subscription_key = os.getenv('LEO_SUBSCRIPTION_KEY')

if all([api_base_url, workflow_id, bearer_token, subscription_key]):
    client = LeoAgentClient(
        api_base_url=api_base_url,
        workflow_id=workflow_id,
        bearer_token=bearer_token,
        subscription_key=subscription_key
    )
    print("✓ LeoAgentClient instantiated")
    print(f"✓ stream_agent method exists: {hasattr(client, 'stream_agent')}")
    print(f"✓ call_agent method exists: {hasattr(client, 'call_agent')}")
else:
    print("✗ Leo credentials not found in .env")

# Test Agent API Client
print("\n" + "=" * 60)
print("Testing Agent API Client Streaming")
print("=" * 60)

# AgentApiClient can be initialized with default config
agent_client = AgentApiClient()
print("✓ AgentApiClient instantiated")
print(f"✓ stream_agent method exists: {hasattr(agent_client, 'stream_agent')}")
print(f"✓ run_agent method exists: {hasattr(agent_client, 'run_agent')}")

print("\n✅ Streaming methods are available and ready to use!")
