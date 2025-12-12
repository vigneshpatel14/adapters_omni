# Automagik Omni - Implementation Roadmap

## Phase 1: Environment Setup ✅ (You are here)

### Completed
- [x] Cloned repository with submodules
- [x] Reviewed architecture and codebase
- [x] Analyzed message flow and key components
- [x] Created comprehensive setup guide

### Current Status
The repository is cloned at `c:\Automagic_Omni\` with:
- FastAPI backend code in `src/`
- Evolution API submodule in `resources/evolution-api`
- Database migrations in `alembic/`
- Configuration template in `.env.example`

---

## Phase 2: API Server Configuration (Next)

### Steps to Execute

#### 2.1 Configure Environment Variables
```bash
cd c:\Automagic_Omni

# Copy template
cp .env.example .env

# Edit .env with your settings:
# - Generate random AUTOMAGIK_OMNI_API_KEY
# - Set Evolution API endpoint
# - Set CORS origins
# - Configure database path
```

**Your Configuration:**
```env
AUTOMAGIK_OMNI_API_KEY="generate-a-random-secure-key"
ENVIRONMENT="development"
LOG_LEVEL="INFO"
AUTOMAGIK_OMNI_API_HOST="0.0.0.0"
AUTOMAGIK_OMNI_API_PORT="8882"
AUTOMAGIK_OMNI_CORS_ORIGINS="http://localhost:3000,http://localhost:8888"
AUTOMAGIK_OMNI_SQLITE_DATABASE_PATH="./data/automagik-omni.db"
AUTOMAGIK_OMNI_ENABLE_TRACING="true"
AUTOMAGIK_TIMEZONE="UTC"
```

#### 2.2 Install Dependencies
```bash
make install
# OR
uv sync
```

This will:
- Install Python dependencies from `pyproject.toml`
- Set up the `uv` virtual environment
- Install Evolution API dependencies (Node.js packages)

#### 2.3 Initialize Database
```bash
make db-init
# OR
uv run python -m alembic upgrade head
```

This will:
- Create SQLite database at configured path
- Run all migrations
- Create tables (InstanceConfig, MessageTrace, etc.)
- Seed initial data if needed

#### 2.4 Start API Server
```bash
make dev
# OR
uv run python -m src.api.app
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8882
INFO:     Application startup complete
```

### Verification
```bash
# Health check
curl http://localhost:8882/health

# Test API key
curl -H "x-api-key: your-api-key" http://localhost:8882/api/v1/instances
```

---

## Phase 3: Echo Agent Creation

### Simple Echo Agent

Create file `agent-echo.py`:

```python
#!/usr/bin/env python3
"""
Simple echo agent for testing Automagik Omni.
Echoes back every message it receives.
"""

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
    """Process a message and return echo response."""
    logger.info(f"Received message from {request.user_id}: {request.message}")
    
    # Simple echo with context
    echo_text = f"[Echo from {request.session_origin}] {request.message}"
    
    logger.info(f"Responding with: {echo_text}")
    return AgentResponse(text=echo_text)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8886, reload=True)
```

Run it:
```bash
python agent-echo.py
```

### Verification
```bash
# Health check
curl http://localhost:8886/health

# Test echo
curl -X POST http://localhost:8886/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "session_id": "session-123",
    "session_name": "Test User",
    "message": "Hello Echo!",
    "session_origin": "whatsapp"
  }'

# Should return: {"text": "[Echo from whatsapp] Hello Echo!"}
```

---

## Phase 4: Create Omni Instance

### Create WhatsApp Instance Pointing to Echo Agent

```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: your-api-key-from-env" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "echo-test",
    "channel_type": "whatsapp",
    "evolution_url": "https://evolution-api-production-7611.up.railway.app",
    "evolution_key": "6976750A654C-4D9A-85B1-90D8E5411FAB",
    "whatsapp_instance": "8b167ecf-b1a6-4165-bb0c-c2c7fbaf103e",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "test-key",
    "default_agent": "echo",
    "agent_timeout": 30
  }'
```

**Response should include:**
```json
{
  "id": 1,
  "name": "echo-test",
  "channel_type": "whatsapp",
  "agent_api_url": "http://localhost:8886",
  "created_at": "2025-12-10T...",
  "is_active": true
}
```

### Verify Instance Creation

```bash
# List instances
curl -H "x-api-key: your-api-key" http://localhost:8882/api/v1/instances

# Get specific instance
curl -H "x-api-key: your-api-key" \
  http://localhost:8882/api/v1/instances/echo-test

# Get QR code (if needed)
curl -H "x-api-key: your-api-key" \
  http://localhost:8882/api/v1/instances/echo-test/qr-code
```

---

## Phase 5: End-to-End Test

### Message Flow Test

1. **Send WhatsApp Message**
   - Send a message from your WhatsApp number to the instance phone

2. **Monitor Omni API Logs**
   - Look for webhook received message
   - Check message routing logs
   - Verify agent call logs

3. **Check Agent Logs**
   - Verify agent received request
   - Confirm agent returned response

4. **Verify WhatsApp Response**
   - You should receive the echoed message back
   - Message should be prefixed with `[Echo from whatsapp]`

5. **Review Message Trace**
   ```bash
   curl -H "x-api-key: your-api-key" \
     "http://localhost:8882/api/v1/traces?instance_name=echo-test&page=1"
   ```

   **Trace should show:**
   - Incoming message received
   - Agent request sent
   - Agent response received
   - Message sent to WhatsApp

### Example Trace Entry

```json
{
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "instance_name": "echo-test",
  "status": "sent",
  "source_channel": "whatsapp",
  "source_user_id": "+1234567890",
  "incoming_payload": {
    "event": "messages.upsert",
    "data": { "message": { "body": "Hello" } }
  },
  "agent_request_payload": {
    "user_id": "+1234567890",
    "message": "Hello",
    "session_origin": "whatsapp"
  },
  "agent_response_payload": {
    "text": "[Echo from whatsapp] Hello"
  },
  "outgoing_payload": {
    "phone": "+1234567890",
    "message": "[Echo from whatsapp] Hello"
  },
  "duration_ms": 245,
  "agent_duration_ms": 12,
  "created_at": "2025-12-10T..."
}
```

---

## Phase 6: Access Control & Security (Optional for Phase 1)

### Add Phone Number Allowlist

```bash
curl -X POST http://localhost:8882/api/v1/access-control \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "echo-test",
    "rule_type": "whitelist",
    "phone_numbers": ["+1234567890", "+9876543210"]
  }'
```

### Add Phone Number Blocklist

```bash
curl -X POST http://localhost:8882/api/v1/access-control \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "echo-test",
    "rule_type": "blacklist",
    "phone_numbers": ["+1111111111"]
  }'
```

---

## Phase 7: Discord Integration (Later)

When ready, Discord support:

1. Create Discord bot in Discord Developer Portal
2. Configure bot token and guild ID
3. Create instance with `channel_type: "discord"`
4. Same message flow works automatically!

---

## Troubleshooting Checklist

- [ ] Omni API running on port 8882?
- [ ] Echo agent running on port 8886?
- [ ] Evolution API reachable (curl the health endpoint)?
- [ ] WhatsApp instance ID correct?
- [ ] API key in requests matches `.env`?
- [ ] Agent response is valid JSON with "text" field?
- [ ] Database migrations completed (no SQLAlchemy errors)?
- [ ] CORS origins configured for your agent URL?
- [ ] Firewall allows localhost:8882 and :8886?

---

## Quick Command Reference

```bash
# Install & Setup
make install          # Install dependencies
make db-init         # Initialize database
make dev            # Start API server

# Testing
curl http://localhost:8882/health
curl http://localhost:8886/health

# Logs
tail -f ./logs/automagik-omni.log

# Database
sqlite3 ./data/automagik-omni.db
# .tables  # List tables
# SELECT * FROM instance_config;

# Clean up
make clean          # Remove build artifacts
```

---

## Success Criteria for Phase 1

✅ Repository cloned and dependencies installed
✅ API server running on port 8882
✅ Database initialized with schema
✅ Echo agent running on port 8886
✅ Omni instance created pointing to echo agent
✅ Message flows end-to-end (WhatsApp → Omni → Echo → WhatsApp)
✅ Message traces show complete lifecycle
✅ All API endpoints responding correctly

Once these are complete, you have a working foundation for:
- Building real agents
- Adding Discord support
- Implementing access control
- Scaling to production
