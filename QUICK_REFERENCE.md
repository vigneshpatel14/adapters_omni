# Automagik Omni - Quick Reference Guide

## Installation & Setup (5 minutes)

```bash
# Clone (done)
cd c:\Automagic_Omni

# Copy and configure
cp .env.example .env
# Edit .env with your API keys and Evolution API details

# Install dependencies
make install

# Initialize database
make db-init

# Start API
make dev
# Listen on: http://0.0.0.0:8882
```

## Environment Variables Cheat Sheet

```env
# REQUIRED
AUTOMAGIK_OMNI_API_KEY=your-random-key-here

# API Server
AUTOMAGIK_OMNI_API_HOST=0.0.0.0
AUTOMAGIK_OMNI_API_PORT=8882
AUTOMAGIK_OMNI_CORS_ORIGINS=http://localhost:3000,http://localhost:8888

# Database (SQLite or PostgreSQL)
AUTOMAGIK_OMNI_SQLITE_DATABASE_PATH=./data/automagik-omni.db
# OR
# AUTOMAGIK_OMNI_DATABASE_URL=postgresql://user:pass@localhost:5432/omni

# Logging
ENVIRONMENT=development
LOG_LEVEL=INFO
AUTOMAGIK_TIMEZONE=UTC

# Tracing
AUTOMAGIK_OMNI_ENABLE_TRACING=true
AUTOMAGIK_OMNI_TRACE_RETENTION_DAYS=30
```

---

## Quick API Calls

### Health Check
```bash
curl http://localhost:8882/health
# {"status": "healthy"}
```

### Create Instance
```bash
API_KEY="your-api-key"
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "echo-test",
    "channel_type": "whatsapp",
    "evolution_url": "https://evolution-api-production-7611.up.railway.app",
    "evolution_key": "6976750A654C-4D9A-85B1-90D8E5411FAB",
    "whatsapp_instance": "8b167ecf-b1a6-4165-bb0c-c2c7fbaf103e",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "test-key",
    "default_agent": "echo"
  }'
```

### List Instances
```bash
curl -H "x-api-key: $API_KEY" http://localhost:8882/api/v1/instances
```

### Get Specific Instance
```bash
curl -H "x-api-key: $API_KEY" http://localhost:8882/api/v1/instances/echo-test
```

### Get Contacts (Omni API)
```bash
curl -H "x-api-key: $API_KEY" \
  "http://localhost:8882/api/v1/echo-test/contacts?page=1&page_size=50"
```

### Send Text Message
```bash
curl -X POST http://localhost:8882/api/v1/echo-test/send-text \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "+1234567890",
    "text": "Hello from Omni!",
    "session_id": "optional"
  }'
```

### Get Message Traces
```bash
curl -H "x-api-key: $API_KEY" \
  "http://localhost:8882/api/v1/traces?instance_name=echo-test&page=1"
```

### Get Specific Trace
```bash
curl -H "x-api-key: $API_KEY" \
  "http://localhost:8882/api/v1/traces/550e8400-e29b-41d4-a716-446655440000"
```

---

## Echo Agent Code (Copy-Paste Ready)

File: `agent-echo.py`

```python
#!/usr/bin/env python3
"""Simple echo agent for testing."""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Echo Agent")

class UserData(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None

class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    session_name: str
    message: str
    message_type: str = "text"
    session_origin: str = "whatsapp"
    user: Optional[UserData] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    text: str

@app.post("/api/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest):
    """Echo endpoint."""
    logger.info(f"Received: {request.message}")
    echo_text = f"[Echo from {request.session_origin}] {request.message}"
    logger.info(f"Responding: {echo_text}")
    return AgentResponse(text=echo_text)

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8886, reload=True)
```

Run:
```bash
python agent-echo.py
```

---

## Project Structure (Key Files)

```
src/
├── api/
│   ├── app.py                          # Main API
│   ├── routes/
│   │   ├── instances.py                # Instance CRUD
│   │   ├── omni.py                     # Unified API
│   │   ├── messages.py                 # Send messages
│   │   └── traces.py                   # View traces
│   └── schemas/                        # Request/response schemas
│
├── channels/
│   ├── whatsapp/
│   │   ├── handlers.py                 # Process WhatsApp messages
│   │   └── evolution_api_sender.py     # Send via Evolution API
│   └── discord/                        # (Future)
│
├── services/
│   ├── message_router.py               # Route to agent
│   ├── agent_api_client.py             # Call your agent
│   ├── trace_service.py                # Log traces
│   └── access_control.py               # ACL
│
├── db/
│   ├── models.py                       # Database models
│   └── migrations.py                   # Alembic migrations
│
└── config.py                           # Configuration
```

---

## Key Database Tables

### InstanceConfig
```
id: INT (PK)
name: STRING (unique)
channel_type: STRING (whatsapp|discord)
is_active: BOOLEAN
agent_api_url: STRING
agent_api_key: STRING (encrypted)
default_agent: STRING
evolution_url: STRING (nullable)
evolution_key: STRING (encrypted)
whatsapp_instance: STRING (nullable)
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

### MessageTrace
```
id: UUID (PK)
trace_id: UUID
instance_id: INT (FK)
status: STRING (sent|error|processing)
source_channel: STRING (whatsapp)
source_user_id: STRING
session_id: STRING (nullable)
incoming_payload: JSON
agent_request_payload: JSON
agent_response_payload: JSON
outgoing_payload: JSON
duration_ms: INT
agent_duration_ms: INT (nullable)
error_message: STRING (nullable)
created_at: TIMESTAMP
```

---

## Typical Message Flow

```
1. User sends WhatsApp message
2. Evolution API webhook → POST /api/v1/webhook/evolution/{instance}
3. Omni processes & extracts text
4. Message Router applies ACL
5. Agent API call → POST /api/agent/chat
6. Your agent responds
7. Omni sends to Evolution API
8. Evolution API → WhatsApp → User's phone
9. Trace logged with full lifecycle
```

**Duration**: 150-500ms (depending on agent response time)

---

## Common Commands

```bash
# Install
make install

# Initialize DB
make db-init

# Start development server
make dev

# Run tests
make test

# Check code
make lint

# Format code
make format

# Clean up
make clean

# List CLI commands
make cli-help
```

---

## Debugging Tips

### Check Logs
```bash
# Live logs
tail -f ./logs/automagik-omni.log

# Filter for errors
grep ERROR ./logs/automagik-omni.log

# Filter for specific instance
grep "echo-test" ./logs/automagik-omni.log
```

### Check Database
```bash
# SQLite shell
sqlite3 ./data/automagik-omni.db

# List tables
.tables

# View instances
SELECT id, name, channel_type, is_active FROM instance_config;

# View traces (last 5)
SELECT trace_id, status, source_user_id, created_at FROM message_trace ORDER BY created_at DESC LIMIT 5;

# Check specific trace
SELECT * FROM message_trace WHERE trace_id = 'xxx';
```

### Test Webhook Manually
```bash
curl -X POST http://localhost:8882/api/v1/webhook/evolution/echo-test \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "message": {
        "key": {
          "id": "test@c.us",
          "fromMe": false,
          "remoteJid": "+1234567890@s.whatsapp.net"
        },
        "message": {
          "conversation": "Test message"
        }
      }
    }
  }'
```

---

## Error Responses

### 400 Bad Request
```json
{"detail": "Invalid request payload"}
```

### 401 Unauthorized
```json
{"detail": "Invalid or missing API key"}
```

### 404 Not Found
```json
{"detail": "Instance not found"}
```

### 500 Server Error
```json
{"detail": "Internal server error (check logs)"}
```

---

## Environment Setup (One-Time)

```bash
# 1. Generate random API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to AUTOMAGIK_OMNI_API_KEY in .env

# 2. Edit .env with:
# - Evolution API URL
# - Evolution API key
# - WhatsApp instance ID
# - CORS origins (your frontend/agent ports)

# 3. Create data directory
mkdir -p ./data

# 4. Install & setup
make install
make db-init

# 5. Start
make dev
# Should see:
# INFO:     Started server process
# INFO:     Application startup complete
```

---

## WhatsApp Flow Summary

```
Your WhatsApp Phone
    ↓ Send message to bot number
    ↓
Evolution API Instance
(8b167ecf-b1a6-4165-bb0c-c2c7fbaf103e)
    ↓ Webhook (auto)
    ↓
Omni API (:8882)
/api/v1/webhook/evolution/echo-test
    ↓ Process
    ↓
Your Agent (:8886)
/api/agent/chat
    ↓ Response
    ↓
Omni API (process response)
    ↓
Evolution API (send)
    ↓
Your WhatsApp Phone
    ↓ Receive echoed message!
```

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| API not starting | Check port 8882 is free, check .env syntax |
| "evolution_url connection refused" | Verify Evolution API URL is reachable |
| "Agent timeout" | Increase agent_timeout, check agent is running |
| "Instance not found" | Create instance first with POST /instances |
| "No response from WhatsApp" | Check trace to see where it failed |
| "Permission denied on database" | Check ./data directory permissions |
| "API key invalid" | Verify x-api-key header matches .env |

---

## Next Steps

1. ✅ Clone repo & review code
2. ⬜ Copy .env.example → .env with your settings
3. ⬜ make install && make db-init
4. ⬜ make dev (start API on :8882)
5. ⬜ Create echo agent (agent-echo.py on :8886)
6. ⬜ Create instance pointing to echo agent
7. ⬜ Send WhatsApp message to test
8. ⬜ Check traces to see full flow
9. ⬜ Replace echo with real agent logic
10. ⬜ Add Discord support (later)

---

## Support Resources

- **Docs**: `/docs/` directory in repo
- **GitHub Issues**: Report bugs on GitHub
- **Discord**: Join community at https://discord.gg/xcW8c7fF3R
- **Roadmap**: https://github.com/orgs/namastexlabs/projects/9/views/1
