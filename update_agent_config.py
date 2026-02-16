#!/usr/bin/env python3
import sqlite3

# Extract from the curl command:
new_url = "https://api-build.gep.com/leo-portal-agentic-runtime-node-api/v1/workflow-engine/99382ebe-86fd-4b54-b1c9-ee42962f858c/stream"
# Bearer token from the curl
bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL2NsYWltcy9hdXRobm1ldGhvZHNyZWZlcmVuY2VzIjpbInB3ZCIsInJzYSIsIm1mYSJdLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zdXJuYW1lIjoiVm9kZGFtIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvZ2l2ZW5uYW1lIjoiVmlnbmVzaCIsImdyb3VwcyI6IjAyODgwYTBlLWVlNjUtNGY1NC1hY2M4LTUwZDU4MDZjZDZhNyIsIm5hbWUiOiJWaWduZXNoIFZvZGRhbSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vaWRlbnRpdHkvY2xhaW1zL29iamVjdGlkZW50aWZpZXIiOiI5YjZlZDIwZS0yOTgzLTQzOWYtYmYzMS1lODFhNmM5ODFkZDEiLCJyaCI6IjEuQVZvQTA1R2k0eUNLTlV5TkNEal95dnBIblNPaXpZYVdJc05HcmtMeEM2ektaSFZXQVVOYUFBLiIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiUDR5ckxVcGVCZG5TbTBHazVNR0FJRGpadGdOWlhVLW9IQTliaXhfQUdkYyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vaWRlbnRpdHkvY2xhaW1zL3RlbmFudGlkIjoiZTNhMjkxZDMtOGEyMC00YzM1LThkMDgtMzhmZmNhZmE0NzlkIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZSI6InZpZ25lc2gudm9kZGFtQGdlcC5jb20iLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy91cG4iOiJ2aWduZXNoLnZvZGRhbUBnZXAuY29tIiwidXRpIjoiMGg1TVByZncxRUtoVWZzMHpia2dBQSIsImF1ZCI6Imh0dHBzOi8vcGxhdGZvcm1kZXYuZ2VwLmNvbS8iLCJleHAiOjE3Njg4MDk1OTEsImlzcyI6Imh0dHBzOi8vYnVpbGQuZ2VwLmNvbS8ifQ.zCNuW2uuiBpD1bCNwzwL30Ty06_sCLFBEm0Xzy4dlwI"
ocp_key = "1cbd622fdcfd4753b4b43be776fe8c3f"

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

# Update pythonassistant instance with new agent configuration
cursor.execute('''
    UPDATE instance_configs
    SET 
        agent_api_url = ?,
        agent_api_key = ?
    WHERE name = 'pythonassistant'
''', (new_url, bearer_token))

conn.commit()
print(f"✅ Updated pythonassistant with new agent endpoint")
print(f"  URL: {new_url}")
print(f"  Auth: Bearer token set")
print(f"  OCP Key (store separately): {ocp_key}")
print(f"  Rows updated: {cursor.rowcount}")

conn.close()
