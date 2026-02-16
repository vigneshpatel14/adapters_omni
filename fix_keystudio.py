#!/usr/bin/env python
"""Update keystudio-knowledge with correct Leo API endpoint from working curl"""

from src.db.database import SessionLocal
from src.db.models import InstanceConfig

db = SessionLocal()

instance = db.query(InstanceConfig).filter(
    InstanceConfig.name == 'keystudio-knowledge'
).first()

if instance:
    # Update with the CORRECT Leo API endpoint (from working curl)
    instance.agent_api_url = "https://api-build.gep.com/leo-portal-agentic-runtime-node-api/v1"
    instance.agent_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL2NsYWltcy9hdXRobm1ldGhvZHNyZWZlcmVuY2VzIjpbInB3ZCIsInJzYSIsIm1mYSJdLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zdXJuYW1lIjoiVm9kZGFtIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvZ2l2ZW5uYW1lIjoiVmlnbmVzaCIsImdyb3VwcyI6IjAyODgwYTBlLWVlNjUtNGY1NC1hY2M4LTUwZDU4MDZjZDZhNyIsIm5hbWUiOiJWaWduZXNoIFZvZGRhbSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vaWRlbnRpdHkvY2xhaW1zL29iamVjdGlkZW50aWZpZXIiOiI5YjZlZDIwZS0yOTgzLTQzOWYtYmYzMS1lODFhNmM5ODFkZDEiLCJyaCI6IjEuQVZvQTA1R2k0eUNLTlV5TkNEal95dnBIblNPaXpZYVdJc05HcmtMeEM2ektaSFZXQVVOYUFBLiIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiUDR5ckxVcGVCZG5TbTBHazVNR0FJRGpadGdOWlhVLW9IQTliaXhfQUdkYyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vaWRlbnRpdHkvY2xhaW1zL3RlbmFudGlkIjoiZTNhMjkxZDMtOGEyMC00YzM1LThkMDgtMzhmZmNhZmE0NzlkIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZSI6InZpZ25lc2gudm9kZGFtQGdlcC5jb20iLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy91cG4iOiJ2aWduZXNoLnZvZGRhbUBnZXAuY29tIiwidXRpIjoiSkFPWW90YldzRUNRVmJyVWFwSTdBQSIsImF1ZCI6Imh0dHBzOi8vcGxhdGZvcm1kZXYuZ2VwLmNvbS8iLCJleHAiOjE3NzA4OTU0NDEsImlzcyI6Imh0dHBzOi8vYnVpbGQuZ2VwLmNvbS8ifQ.ukkAwSguHTld0eij4PYlzLBPeToUNDOnmYPlM99LWkI"
    
    db.commit()
    
    print("✅ Updated keystudio-knowledge!")
    print(f"   Agent API URL: {instance.agent_api_url}")
    print(f"   Agent API Key: Set ✓")
    print("\n📝 Configuration updated to use:")
    print("   - api-build.gep.com endpoint")
    print("   - New bearer token")
    print("   - Workflow ID: 99382ebe-86fd-4b54-b1c9-ee42962f858c")
else:
    print("❌ Instance not found")

db.close()
