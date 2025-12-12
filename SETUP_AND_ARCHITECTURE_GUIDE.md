# Automagik Omni - Setup & Architecture Guide

## Overview

**Automagik Omni** is a multi-tenant, omnichannel messaging hub that routes messages from WhatsApp, Discord, and other platforms to your custom AI agents. It provides:

- 🔌 **Unified API** for all supported channels (WhatsApp, Discord, Slack, etc.)
- 🏢 **Multi-tenant architecture** with complete isolation between instances
- 📊 **Message tracing** with full lifecycle visibility
- 🔐 **Enterprise security** with API keys, request validation, and CORS
- 🤖 **MCP-native support** for Claude and other AI tools
- 🚀 **Production-ready** with SQLite or PostgreSQL support

---

## Architecture Overview

### Message Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  EXTERNAL CHANNELS (WhatsApp, Discord, Slack)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Evolution API│  │Discord Bots  │  │ Slack API    │          │
│  │ (WhatsApp)   │  │              │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          │ Webhook/IPC      │ IPC             │ Webhook
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  AUTOMAGIK OMNI API (FastAPI, Port 8882)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ API Routes:                                                │ │
│  │ - POST /api/v1/webhook/evolution/{instance}  (WhatsApp)   │ │
│  │ - POST /api/v1/instances                     (Management) │ │
│  │ - GET /api/v1/{instance}/contacts           (Omni API)   │ │
│  │ - GET /api/v1/{instance}/chats               (Omni API)   │ │
│  │ - POST /api/v1/{instance}/send-text         (Sending)    │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Services Layer:                                            │ │
│  │ - Message Router: Routes to appropriate agent              │ │
│  │ - Agent Service: Coordinates agent interactions            │ │
│  │ - Trace Service: Logs message lifecycle                    │ │
│  │ - Access Control: Permission & ACL checks                 │ │
│  │ - User Service: User/session management                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          │ HTTP POST
          ▼
┌─────────────────────────────────────────────────────────────────┐
│  YOUR AGENT ENDPOINT (Port configurable, e.g., 8886)            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ POST /api/agent/chat                                       │ │
│  │ Receives: {user_id, session_id, message, context}        │ │
│  │ Returns: {response_text, actions}                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          │ Response
          ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACK TO OMNI API → CHANNELS → USER                             │
│                                                                  │
│  1. Agent response processed                                    │
│  2. Message routed back to channel handler                      │
│  3. Evolution API/Discord/Slack sends to user                   │
│  4. Trace logged with full lifecycle                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
automagik-omni/
├── src/
│   ├── api/                          # FastAPI application
│   │   ├── app.py                   # Main FastAPI app with middleware
│   │   ├── deps.py                  # Dependency injection (auth, DB)
│   │   ├── routes/
│   │   │   ├── instances.py         # CRUD for instance configs
│   │   │   ├── omni.py              # Unified channel API
│   │   │   ├── messages.py          # Message sending
│   │   │   ├── access.py            # Permission management
│   │   │   └── traces.py            # Message trace viewing
│   │   └── schemas/                 # Pydantic models for API
│   │
│   ├── channels/                     # Channel-specific handlers
│   │   ├── base.py                  # Abstract base classes
│   │   ├── omni_base.py             # Omni API base handler
│   │   ├── whatsapp/                # WhatsApp via Evolution API
│   │   │   ├── channel_handler.py   # Instance creation/QR
│   │   │   ├── handlers.py          # Message processing
│   │   │   ├── evolution_api_sender.py  # Message sending
│   │   │   └── evolution_api_client.py  # Evolution API client
│   │   ├── discord/                 # Discord bot integration
│   │   │   ├── bot_manager.py       # Discord bot lifecycle
│   │   │   └── ipc_client.py        # Unix socket client
│   │   └── handlers/                # Omni implementations
│   │       ├── whatsapp_chat_handler.py
│   │       └── discord_chat_handler.py
│   │
│   ├── services/                     # Business logic
│   │   ├── agent_service.py         # Agent coordination
│   │   ├── agent_api_client.py      # Call your agent endpoint
│   │   ├── message_router.py        # Route messages to agents
│   │   ├── trace_service.py         # Message tracing
│   │   ├── access_control.py        # ACL & permissions
│   │   ├── user_service.py          # User management
│   │   └── discovery_service.py     # Dynamic service discovery
│   │
│   ├── db/                           # Database layer
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── database.py              # DB connection & sessions
│   │   ├── migrations.py            # Alembic migrations
│   │   └── seed_db.py               # Seed data
│   │
│   ├── cli/                          # CLI commands
│   │   └── main.py                  # CLI entry point
│   │
│   ├── config.py                     # Config management
│   ├── logger.py                     # Logging setup
│   └── version.py                    # Version info
│
├── alembic/                          # Database migrations
├── docs/                             # Documentation
├── tests/                            # Test suite
├── .env.example                      # Environment template
├── Makefile                          # Development commands
├── pyproject.toml                    # Python dependencies
└── README.md                         # Quick start
```

---

## Key Components Explained

### 1. **API Layer** (`src/api/`)

The FastAPI application handles:

- **Authentication**: `verify_api_key()` dependency checks `x-api-key` header
- **CORS**: Configured via `AUTOMAGIK_OMNI_CORS_ORIGINS`
- **Request Logging**: All requests logged with payloads (non-sensitive)
- **Telemetry**: Optional usage tracking

**Main Routes:**
- `POST /api/v1/instances` - Create/update instances
- `POST /api/v1/webhook/evolution/{instance_name}` - WhatsApp webhooks
- `GET /api/v1/{instance}/contacts` - Unified contacts API
- `POST /api/v1/{instance}/send-text` - Send messages

### 2. **Channels Layer** (`src/channels/`)

Each channel (WhatsApp, Discord, Slack) has:

- **Handler**: Manages instance creation, QR codes, status
- **Omni Handler**: Implements unified API (contacts, chats, etc.)
- **Message Processors**: Handle incoming messages
- **Senders**: Send messages back to users

**WhatsApp Flow:**
```
Evolution API Webhook
    ↓
POST /webhook/evolution/{instance}
    ↓
WhatsApp Message Handler (handlers.py)
    ↓
Extract text/media, transcribe audio
    ↓
Message Router → Agent Service
    ↓
POST to Agent Endpoint (your code)
    ↓
Evolution API Sender → WhatsApp User
    ↓
Trace Service logs entire lifecycle
```

### 3. **Services Layer** (`src/services/`)

**Message Router**
- Routes messages to the correct agent
- Handles user creation/session management
- Applies access control rules
- Supports both sync and streaming responses

**Agent Service**
- Coordinates agent interactions
- Handles audio transcription
- Manages timeouts and retries

**Trace Service**
- Logs every message through the system
- Records performance metrics
- Stores payloads for debugging
- Retention configurable (default: 30 days)

**Access Control**
- Per-phone-number allowlists/blocklists
- Instance-level ACLs
- Token-based authorization

### 4. **Database Layer** (`src/db/`)

**Core Models:**
- `InstanceConfig` - Channel instance (WhatsApp phone, Discord guild, etc.)
- `MessageTrace` - Message lifecycle logging
- `AccessControl` - Permission rules
- `UserSession` - User/session tracking

**Migrations**: Alembic automatically runs on startup

---

## Configuration

### Environment Variables (`.env`)

**Required:**
```bash
# API Authentication
AUTOMAGIK_OMNI_API_KEY="your-secure-random-key-here"

# Evolution API (WhatsApp)
EVOLUTION_API_KEY="your-evolution-api-key"
```

**Common:**
```bash
# API Server
AUTOMAGIK_OMNI_API_HOST="0.0.0.0"
AUTOMAGIK_OMNI_API_PORT="8882"
AUTOMAGIK_OMNI_CORS_ORIGINS="http://localhost:3000,http://localhost:8888"

# Database
AUTOMAGIK_OMNI_SQLITE_DATABASE_PATH="./data/automagik-omni.db"
# OR for PostgreSQL:
# AUTOMAGIK_OMNI_DATABASE_URL="postgresql://user:pass@localhost:5432/automagik_omni"

# Logging
LOG_LEVEL="INFO"
ENVIRONMENT="development"
AUTOMAGIK_TIMEZONE="UTC"

# Tracing
AUTOMAGIK_OMNI_ENABLE_TRACING="true"
AUTOMAGIK_OMNI_TRACE_RETENTION_DAYS="30"
```

### Instance Configuration

Create an instance via API:

```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-whatsapp-bot",
    "channel_type": "whatsapp",
    "evolution_url": "https://your-evolution-api.com",
    "evolution_key": "YOUR_EVOLUTION_KEY",
    "whatsapp_instance": "8b167ecf-b1a6-4165-bb0c-c2c7fbaf103e",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "your-agent-key",
    "default_agent": "your-agent-name",
    "agent_timeout": 60
  }'
```

**WhatsApp-Specific Fields:**
- `evolution_url` - Your Evolution API instance URL
- `evolution_key` - Evolution API authentication key
- `whatsapp_instance` - Instance UUID from Evolution API

**Agent Configuration:**
- `agent_api_url` - Your agent endpoint (e.g., Automagik Hive, custom service)
- `agent_api_key` - Authentication for your agent
- `default_agent` - Agent name/ID to use
- `agent_timeout` - Timeout in seconds (default: 60)

---

## Message Lifecycle

### 1. **Incoming Message** (WhatsApp Example)

```
User sends WhatsApp message
    ↓
Evolution API receives message
    ↓
Evolution API POST to: http://omni:8882/api/v1/webhook/evolution/{instance_name}
    ↓
Request logged + trace created
    ↓
WhatsApp Message Handler processes:
  - Extract text/media
  - Transcribe audio (if present)
  - Normalize phone number
  - Create/get user session
```

### 2. **Message Routing**

```
Message Router:
  - Applies access control (allow/block list)
  - Gets instance configuration
  - Retrieves or creates user session
  - Prepares agent payload
```

### 3. **Agent Call**

```
POST to Agent Endpoint:
{
  "user_id": "123456789",
  "session_id": "session-abc123",
  "session_name": "+1234567890",
  "message": "Hello!",
  "message_type": "text",
  "session_origin": "whatsapp",
  "user": {
    "phone_number": "+1234567890",
    "email": null,
    "user_data": {}
  },
  "context": {
    "channel": "whatsapp",
    "instance": "my-whatsapp-bot"
  }
}

Agent processes and responds:
{
  "text": "Hello! How can I help?",
  "media": [optional media items],
  "actions": [optional actions]
}
```

### 4. **Response Handling**

```
Agent Response received
    ↓
Message formatter processes response
    ↓
IF message > 1000 chars:
  SPLIT on double newlines (if enabled)
    ↓
SEND each chunk to Evolution API
    ↓
Evolution API sends to WhatsApp user
    ↓
Trace logged with final status
```

### 5. **Message Trace**

Complete trace includes:
- Incoming message (source)
- Processing steps
- Agent request/response
- Channel send confirmation
- Performance metrics
- Any errors encountered

---

## Setting Up Your Echo Agent

For testing, you'll create a simple FastAPI service that echoes back messages.

### Minimal Echo Agent (`agent-echo.py`)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    session_name: str
    message: str
    message_type: str = "text"
    session_origin: str = "whatsapp"

class AgentResponse(BaseModel):
    text: str

@app.post("/api/agent/chat")
async def chat(request: AgentRequest):
    """Echo the user's message back."""
    return AgentResponse(
        text=f"Echo: {request.message}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8886)
```

Run it:
```bash
python agent-echo.py
```

### Create Omni Instance Pointing to Echo Agent

```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: your-api-key" \
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

Now:
1. Send a message to your WhatsApp number
2. Evolution API webhooks to Omni
3. Omni calls your echo agent
4. Echo agent returns the echoed message
5. Omni sends back to WhatsApp
6. You see your message echoed!

---

## API Endpoints Reference

### Instance Management

```bash
# Create instance
POST /api/v1/instances
Headers: x-api-key: <key>
Body: { name, channel_type, evolution_url, evolution_key, agent_api_url, ... }

# List instances
GET /api/v1/instances
Headers: x-api-key: <key>

# Get instance
GET /api/v1/instances/{instance_name}
Headers: x-api-key: <key>

# Update instance
PUT /api/v1/instances/{instance_name}
Headers: x-api-key: <key>
Body: { agent_api_url, agent_api_key, ... }

# Delete instance
DELETE /api/v1/instances/{instance_name}
Headers: x-api-key: <key>

# Get QR code (WhatsApp)
GET /api/v1/instances/{instance_name}/qr-code
Headers: x-api-key: <key>

# Get connection status
GET /api/v1/instances/{instance_name}/status
Headers: x-api-key: <key>
```

### Omni API (Unified)

```bash
# Get contacts
GET /api/v1/{instance_name}/contacts?page=1&page_size=50
Headers: x-api-key: <key>

# Get chats
GET /api/v1/{instance_name}/chats?page=1&page_size=50
Headers: x-api-key: <key>

# Get channels
GET /api/v1/{instance_name}/channels
Headers: x-api-key: <key>
```

### Message Management

```bash
# Send text message
POST /api/v1/{instance_name}/send-text
Headers: x-api-key: <key>
Body: {
  recipient: "+1234567890",
  text: "Hello!",
  session_id: "optional-session-id"
}

# Send media
POST /api/v1/{instance_name}/send-media
Headers: x-api-key: <key>
Body: {
  recipient: "+1234567890",
  media_url: "https://example.com/image.jpg",
  caption: "optional-caption"
}
```

### Traces

```bash
# Get message traces
GET /api/v1/traces?instance_name=my-bot&page=1
Headers: x-api-key: <key>

# Get trace details
GET /api/v1/traces/{trace_id}
Headers: x-api-key: <key>
```

### Webhook Receivers

```bash
# WhatsApp/Evolution API webhook
POST /api/v1/webhook/evolution/{instance_name}
Body: { event, data, ... } (from Evolution API)
```

---

## Database Schema

### InstanceConfig Table

```
id: Integer (PK)
name: String (unique)
channel_type: String (whatsapp|discord|slack)
is_active: Boolean
created_at: DateTime
updated_at: DateTime

-- WhatsApp specific
evolution_url: String (nullable)
evolution_key: String (encrypted)
whatsapp_instance: String (nullable)

-- Discord specific
discord_bot_token: String (encrypted, nullable)
discord_client_id: String (nullable)
discord_guild_id: String (nullable)

-- Agent configuration
agent_api_url: String
agent_api_key: String (encrypted)
default_agent: String
agent_timeout: Integer

-- UI identification
automagik_instance_id: String (nullable)
automagik_instance_name: String (nullable)

-- Message control
enable_auto_split: Boolean (default: true)
```

### MessageTrace Table

```
id: UUID (PK)
instance_id: Integer (FK)
trace_id: UUID (unique)
created_at: DateTime
status: String (processing|sent|error)
source_channel: String (whatsapp|discord)
source_user_id: String
session_id: String (nullable)

-- Payloads
incoming_payload: JSON
agent_request_payload: JSON (nullable)
agent_response_payload: JSON (nullable)
outgoing_payload: JSON (nullable)

-- Performance
duration_ms: Integer
agent_duration_ms: Integer (nullable)

-- Error info
error_message: String (nullable)
error_traceback: String (nullable)
```

---

## Testing the Setup

### 1. Verify API is Running

```bash
curl http://localhost:8882/health
# Should return: {"status": "healthy"}
```

### 2. Verify API Key Works

```bash
curl -H "x-api-key: your-api-key" http://localhost:8882/api/v1/instances
# Should return: { "instances": [...] }
```

### 3. Test WhatsApp Webhook Manually

```bash
curl -X POST http://localhost:8882/api/v1/webhook/evolution/echo-test \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "message": {
        "conversation": "+1234567890",
        "id": "test-123",
        "timestamp": 1234567890,
        "fromMe": false,
        "body": "Test message from webhook"
      }
    }
  }'
```

### 4. Check Message Traces

```bash
curl -H "x-api-key: your-api-key" \
  "http://localhost:8882/api/v1/traces?instance_name=echo-test&page=1"
```

---

## Common Issues & Solutions

### "evolution_url connection refused"
- Verify Evolution API is running: `curl https://evolution-api-production-7611.up.railway.app/health`
- Check firewall/CORS if remote
- Ensure `evolution_url` in instance config is correct

### "Agent timeout error"
- Increase `agent_timeout` when creating instance
- Check your agent endpoint is responding
- Look at agent service logs

### "WhatsApp QR code not appearing"
- Ensure Evolution API WebSocket is connected
- Evolution API must be kept alive (PM2 or similar)
- QR codes expire after ~2 minutes

### "Message not reaching WhatsApp user"
- Check instance `is_active=true`
- Verify Evolution API has valid WhatsApp session
- Look at message traces for errors
- Check agent response is valid JSON

### "Traces showing but no message sent"
- Check agent response format is correct
- Verify Evolution API can reach WhatsApp
- Check Evolution API logs for send errors

---

## Next Steps

1. **Set up the echo agent** (see section above)
2. **Create Omni instance** pointing to echo agent
3. **Test message flow** by sending WhatsApp message
4. **Check traces** to verify end-to-end flow
5. **Replace echo agent** with real agent logic
6. **Add Discord support** (if needed)
7. **Set up access control** (allowlists/blocklists)

---

## Key Files to Review

For deeper understanding:

1. **Message Flow**: `src/channels/whatsapp/handlers.py` (incoming) → `src/services/message_router.py` (routing) → `src/services/agent_service.py` (agent call)

2. **Response Handling**: `src/channels/whatsapp/evolution_api_sender.py` (sending back to WhatsApp)

3. **Tracing**: `src/services/trace_service.py` (lifecycle logging)

4. **API Routes**: `src/api/routes/omni.py` (unified API), `src/api/routes/instances.py` (management)

5. **Configuration**: `src/config.py` (env loading), `.env.example` (all options)

---

## Resources

- **GitHub**: https://github.com/namastexlabs/automagik-omni
- **Discord**: https://discord.gg/xcW8c7fF3R
- **Roadmap**: https://github.com/orgs/namastexlabs/projects/9/views/1
- **Evolution API Docs**: https://github.com/namastexlabs/evolution-api
