# 🎉 Leo Agent Integration - Complete Summary

**Updated:** December 19, 2025  
**Status:** Production Ready ✅

---

## What Changed?

### ❌ **Old Architecture (Deprecated)**
```
WhatsApp → Evolution API → Omni → adapter-leo-agent.py (port 8887) → Leo API
```
- Separate FastAPI service running on port 8887
- Requires `adapter-leo-agent.py` running
- Separate `.env.leo` configuration file
- Additional process to manage

### ✅ **New Architecture (Current)**
```
WhatsApp → Evolution API → Omni (port 8882) → Leo API
                          ↓
                  LeoAgentClient (built-in)
                  Reads credentials from .env
```
- **Single service:** Omni on port 8882 only
- **Built-in integration:** No separate adapter needed
- **Centralized config:** All in one `.env` file
- **Auto-detection:** Omni detects Leo URLs automatically

---

## Files to Remove

You can safely delete:
- ✂️ `adapter-leo-agent.py` (no longer needed)
- ✂️ `.env.leo` (config moved to main .env)
- ✂️ `.env.leo-adapter` (template file)

---

## Configuration

### .env File (Main Configuration)

All Leo credentials now go in `.env`:

```bash
# Leo API Base URL
LEO_API_BASE_URL="https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1"

# Leo Workflow ID
LEO_WORKFLOW_ID="e9f65742-8f61-4a7f-b0d2-71b77c5391e7"

# Leo Bearer Token (OAuth 2.0 JWT)
LEO_BEARER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6..."

# Leo Subscription Key (Azure API Management)
LEO_SUBSCRIPTION_KEY="018ca54b6f5743bfa732ad309adf9e8f"

# Leo Request Parameters
LEO_BPC="20210511"
LEO_ENVIRONMENT="DEV"
LEO_VERSION="74d530a1-8dc8-443a-977b-1fc34434e806"
```

---

## Creating a WhatsApp Instance with Leo

### Postman Request

```json
POST http://localhost:8882/api/v1/instances

{
  "name": "whatsapp-leo-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "YOUR_EVOLUTION_KEY",
  "agent_api_url": "https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1/workflow-engine/e9f65742-8f61-4a7f-b0d2-71b77c5391e7/stream",
  "agent_api_key": "leo_builtin",
  "default_agent": "leo",
  "agent_timeout": 120,
  "webhook_base64": true,
  "auto_qr": true
}
```

**Key Points:**
- `agent_api_url`: Set to Leo's streaming endpoint
- Omni **auto-detects** the Leo URL (contains "api-leodev.gep.com")
- Uses built-in `LeoAgentClient` 
- Credentials from `.env` are used automatically

---

## How It Works

### 1. **Webhook Received**
   WhatsApp message → Evolution API → Omni webhook handler

### 2. **Auto-Detection**
   Omni checks `agent_api_url` in instance config
   - If contains "api-leodev.gep.com" → Use LeoAgentClient ✅
   - Otherwise → Use generic HTTP agent

### 3. **Agent Call**
   LeoAgentClient (built-in):
   - Reads credentials from `.env`
   - Builds Leo request format
   - Calls Leo streaming API
   - Parses SSE response

### 4. **Response Handling**
   - Collects SSE deltas from Leo
   - Assembles into complete response
   - Returns to Omni response handler
   - Sends to WhatsApp via Evolution API

---

## Benefits of This Architecture

✅ **Simplified Setup**
- One service to manage (Omni)
- No separate adapter process

✅ **Better Performance**
- Direct communication (no proxy)
- Reduced network hops

✅ **Easier Maintenance**
- Single codebase
- Centralized configuration
- Unified logging

✅ **Better Integration**
- Built-in service
- Access to Omni's database
- Unified trace logging

---

## Running Omni with Leo

```bash
# Terminal
cd C:\Automagic_Omni

# Make sure .env has Leo credentials
type .env | findstr LEO_

# Start Omni (Leo integrated)
python -m src

# Output should show:
# ✓ Leo credentials loaded from .env
# ✓ LeoAgentClient initialized
# ✓ API server running on http://0.0.0.0:8882
```

---

## Testing the Integration

### 1. Check Omni Health
```bash
curl http://localhost:8882/health \
  -H "x-api-key: omni-dev-key-test-2025"
```

### 2. Create Instance
```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: omni-dev-key-test-2025" \
  -H "Content-Type: application/json" \
  -d '{...instance_config...}'
```

### 3. Test Webhook
```bash
curl -X POST http://localhost:8882/webhook/evolution/whatsapp-leo-bot \
  -H "Content-Type: application/json" \
  -d '{...message_payload...}'
```

### 4. Check Traces
```bash
curl "http://localhost:8882/api/v1/traces?instance_name=whatsapp-leo-bot&limit=1" \
  -H "x-api-key: omni-dev-key-test-2025"

# Get full payloads
curl "http://localhost:8882/api/v1/traces/{trace_id}/payloads?include_payload=true" \
  -H "x-api-key: omni-dev-key-test-2025"
```

---

## Documentation Updates

Updated docs to reflect new architecture:
- ✅ `COMPLETE_SETUP_AND_CONFIGURATION_GUIDE.md`
- ✅ `POSTMAN_TESTING_GUIDE.md`
- ✅ `.env.example` (added Leo section)

---

## Message Flow Diagram

See `FLOW_DIAGRAM.md` for complete Mermaid sequence diagram showing:
- Webhook received
- Agent request format
- SSE streaming response
- Evolution send
- Complete trace payloads

---

## Quick Reference

| Aspect | Old | New |
|--------|-----|-----|
| **Services** | 2 (Omni + Adapter) | 1 (Omni only) |
| **Ports** | 8882 + 8887 | 8882 |
| **Config Files** | .env + .env.leo | .env only |
| **Adapter Code** | adapter-leo-agent.py | Built-in LeoAgentClient |
| **Startup** | `python -m src` + `python adapter-leo-agent.py` | `python -m src` |
| **Process Count** | 2 | 1 |

---

## Questions?

Refer to:
- **Architecture:** See `FLOW_DIAGRAM.md`
- **Setup:** See `COMPLETE_SETUP_AND_CONFIGURATION_GUIDE.md`
- **API Testing:** See `POSTMAN_TESTING_GUIDE.md`
- **Traces:** Use `/api/v1/traces/{trace_id}/payloads?include_payload=true`

---

**Happy messaging! 🚀**
