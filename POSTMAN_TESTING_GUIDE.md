# 🧪 Complete Postman Testing Guide - Step by Step

**Date:** December 12, 2025  
**Status:** Production Ready  
**Testing Environment:** Local (localhost)

---

## 📋 Table of Contents

1. [Setup & Configuration](#setup--configuration)
2. [Test 1: Echo Agent Health Check](#test-1-echo-agent-health-check)
3. [Test 2: Omni API Health Check](#test-2-omni-api-health-check)
4. [Test 3: Create WhatsApp Instance](#test-3-create-whatsapp-instance)
5. [Test 4: List All Instances](#test-4-list-all-instances)
6. [Test 5: Get Single Instance Details](#test-5-get-single-instance-details)
7. [Test 6: Get WhatsApp QR Code](#test-6-get-whatsapp-qr-code)
8. [Test 7: Send Test Message to Webhook](#test-7-send-test-message-to-webhook)
9. [Test 8: Check Message Traces](#test-8-check-message-traces)
10. [Test 9: Complete Message Flow](#test-9-complete-message-flow)
11. [Test 10: Discord Instance Setup](#test-10-discord-instance-setup)
12. [Troubleshooting](#troubleshooting)

---

## Setup & Configuration

### Prerequisites

- ✅ Postman installed ([Download here](https://www.postman.com/downloads/))
- ✅ Echo Agent running on `localhost:8886`
- ✅ Omni API running on `localhost:8882`
- ✅ PostgreSQL or SQLite database initialized

### Postman Environment Variables (Optional but Recommended)

**Setup in Postman:**
1. Click "Environments" (left sidebar)
2. Click "Create Environment"
3. Name: `Omni-Local`
4. Add variables:

```
OMNI_URL       = http://localhost:8882
AGENT_URL      = http://localhost:8886
API_KEY        = omni-dev-key-test-2025
EVOLUTION_URL  = https://evolution-api-production-7611.up.railway.app
EVOLUTION_KEY  = FA758317-709D-4BB6-BA4F-987B2335036A
```

5. Click "Save"
6. Select this environment in top-right dropdown

**Then use in requests:**
- Instead of: `http://localhost:8882/api/v1/instances`
- Use: `{{OMNI_URL}}/api/v1/instances`

---

## Test 1: Echo Agent Health Check

### Purpose
Verify that the Echo Agent is running and responding correctly.

### Postman Request

**Method:** `GET`

**URL:**
```
http://localhost:8886/health
```

**Headers:**
```
Content-Type: application/json
```

**Body:** (None - GET request)

### Step-by-Step in Postman

1. Click "+" to create new tab
2. Change method dropdown from `GET` (should already be selected)
3. Paste URL: `http://localhost:8886/health`
4. Click "Headers" tab
5. Add header:
   - Key: `Content-Type`
   - Value: `application/json`
6. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
{
  "status": "healthy",
  "service": "echo-agent",
  "version": "1.0.0"
}
```

### What This Tests

✅ Echo Agent is running  
✅ Network connectivity from your machine to agent  
✅ Agent can respond to requests  

---

## Test 2: Omni API Health Check

### Purpose
Verify that Omni API is running and accessible.

### Postman Request

**Method:** `GET`

**URL:**
```
http://localhost:8882/health
```

**Headers:**
```
Content-Type: application/json
```

**Body:** (None)

### Step-by-Step in Postman

1. Create new tab
2. Method: `GET`
3. URL: `http://localhost:8882/health`
4. Headers:
   - Key: `Content-Type`
   - Value: `application/json`
5. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "2.0.0"
}
```

### What This Tests

✅ Omni API server is running  
✅ Database connection is active  
✅ API is ready to receive requests  

---

## Test 3: Create WhatsApp Instance

### Purpose
Create a new WhatsApp instance configured to use Echo Agent.

### Postman Request

**Method:** `POST`

**URL:**
```
http://localhost:8882/api/v1/instances
```

**Headers:**
```
Content-Type: application/json
x-api-key: omni-dev-key-test-2025
```

**Body (Raw JSON):**
```json
{
  "name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "FA758317-709D-4BB6-BA4F-987B2335036A",
  "whatsapp_instance": "whatsapp-bot",
  "session_id_prefix": "whatsapp-bot-",
  "webhook_base64": true,
  "agent_api_url": "http://localhost:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "agent_timeout": 60,
  "enable_auto_split": true
}
```

### Step-by-Step in Postman

1. Create new tab
2. Method: `POST`
3. URL: `http://localhost:8882/api/v1/instances`
4. Click "Headers" tab
5. Add two headers:
   ```
   Key: Content-Type
   Value: application/json
   
   Key: x-api-key
   Value: omni-dev-key-test-2025
   ```
6. Click "Body" tab
7. Select "raw"
8. Change dropdown from "Text" to "JSON"
9. Paste the JSON body above
10. Click "Send"

### Expected Response

**Status:** `201 Created`

```json
{
  "id": 1,
  "name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "FA758317-709D-4BB6-BA4F-987B2335036A",
  "whatsapp_instance": "whatsapp-bot",
  "agent_api_url": "http://localhost:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "agent_timeout": 60,
  "is_active": true,
  "created_at": "2025-12-12T10:30:00.123456"
}
```

### What This Tests

✅ Omni API instance creation working  
✅ Database is saving instance configuration  
✅ Authentication (API key) is working  
✅ Instance is active and ready  

### Fields Explained

| Field | Purpose | Value |
|-------|---------|-------|
| `name` | Unique instance identifier | `whatsapp-bot` |
| `channel_type` | Which channel this is | `whatsapp` |
| `evolution_url` | WhatsApp gateway URL | `https://evolution-api-production-7611.up.railway.app` |
| `evolution_key` | Authentication for Evolution API | Your Evolution API key |
| `agent_api_url` | Where agent is running | `http://localhost:8886` |
| `agent_api_key` | Authentication for agent | `echo-test-key` |
| `default_agent` | Which agent to use | `echo` |
| `agent_timeout` | Timeout in seconds | `60` |

---

## Test 4: List All Instances

### Purpose
Verify that the instance was created and retrieve all instances.

### Postman Request

**Method:** `GET`

**URL:**
```
http://localhost:8882/api/v1/instances
```

**Headers:**
```
x-api-key: omni-dev-key-test-2025
Content-Type: application/json
```

**Body:** (None)

### Step-by-Step in Postman

1. Create new tab
2. Method: `GET`
3. URL: `http://localhost:8882/api/v1/instances`
4. Headers:
   ```
   Key: x-api-key
   Value: omni-dev-key-test-2025
   
   Key: Content-Type
   Value: application/json
   ```
5. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "whatsapp-bot",
    "channel_type": "whatsapp",
    "is_active": true,
    "agent_api_url": "http://localhost:8886",
    "created_at": "2025-12-12T10:30:00.123456"
  }
]
```

### What This Tests

✅ Instance was successfully created  
✅ Database query is working  
✅ Multiple instances can be listed  

---

## Test 5: Get Single Instance Details

### Purpose
Get detailed information about a specific instance.

### Postman Request

**Method:** `GET`

**URL:**
```
http://localhost:8882/api/v1/instances/whatsapp-bot
```

**Headers:**
```
x-api-key: omni-dev-key-test-2025
Content-Type: application/json
```

**Body:** (None)

### Step-by-Step in Postman

1. Create new tab
2. Method: `GET`
3. URL: `http://localhost:8882/api/v1/instances/whatsapp-bot`
4. Headers: (same as Test 4)
5. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
{
  "id": 1,
  "name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "FA758317-709D-4BB6-BA4F-987B2335036A",
  "whatsapp_instance": "whatsapp-bot",
  "agent_api_url": "http://localhost:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "is_active": true,
  "created_at": "2025-12-12T10:30:00.123456",
  "updated_at": "2025-12-12T10:30:00.123456"
}
```

### What This Tests

✅ Instance lookup by name is working  
✅ All configuration fields are stored and retrievable  
✅ Instance is properly initialized  

---

## Test 6: Get WhatsApp QR Code

### Purpose
Generate QR code for WhatsApp authentication.

### Postman Request

**Method:** `GET`

**URL:**
```
http://localhost:8882/api/v1/instances/whatsapp-bot/qr
```

**Headers:**
```
x-api-key: omni-dev-key-test-2025
```

**Body:** (None)

### Step-by-Step in Postman

1. Create new tab
2. Method: `GET`
3. URL: `http://localhost:8882/api/v1/instances/whatsapp-bot/qr`
4. Headers:
   ```
   Key: x-api-key
   Value: omni-dev-key-test-2025
   ```
5. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
{
  "qr": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQMA...",
  "instance_name": "whatsapp-bot",
  "status": "WAITING",
  "expires_in": 60
}
```

### What This Tests

✅ Evolution API communication is working  
✅ QR code generation is working  
✅ Instance can be authenticated  

### How to View QR Code

**Option 1: Copy to Browser**
1. Copy the entire `qr` value (including `data:image/png;base64,`)
2. Open new browser tab
3. Paste in URL bar and press Enter
4. QR code will display
5. Scan with WhatsApp phone

**Option 2: Save as File**
1. Copy just the base64 part (after `data:image/png;base64,`)
2. Visit https://www.base64topdf.com (they have image converter too)
3. Paste base64 string
4. Download as PNG
5. Scan with phone

---

## Test 7: Send Test Message to Webhook

### Purpose
Simulate WhatsApp sending a message to Omni webhook. This tests the complete message flow.

### Postman Request

**Method:** `POST`

**URL:**
```
http://localhost:8882/webhook/evolution/whatsapp-bot
```

**Headers:**
```
Content-Type: application/json
```

**Body (Raw JSON):**
```json
{
  "event": "messages.upsert",
  "data": {
    "messages": [
      {
        "key": {
          "remoteJid": "919014456421@s.whatsapp.net",
          "id": "test_msg_001",
          "fromMe": false
        },
        "message": {
          "conversation": "Hello Omni! Can you echo this back?"
        },
        "messageTimestamp": 1702390000,
        "pushName": "Vignesh",
        "status": "PENDING"
      }
    ]
  }
}
```

### Step-by-Step in Postman

1. Create new tab
2. Method: `POST`
3. URL: `http://localhost:8882/webhook/evolution/whatsapp-bot`
4. Headers:
   ```
   Key: Content-Type
   Value: application/json
   ```
5. Body tab:
   - Select "raw"
   - Change to "JSON"
   - Paste the JSON body
6. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
{
  "status": "success",
  "instance": "whatsapp-bot",
  "trace_id": "ff1ff0da-c57b-429b-a378-d4a242a4ef29"
}
```

### Message Flow (What Happens)

```
1. Postman sends webhook → Omni receives (status 200)
2. Omni extracts message: "Hello Omni! Can you echo this back?"
3. Omni creates trace record
4. Omni routes to agent: agent_api_url = http://localhost:8886
5. Agent (Echo) processes and returns: "Echo: Hello Omni! Can you echo this back?"
6. Omni would send back to Evolution API (WhatsApp)
7. Trace marked as "completed"
```

### What This Tests

✅ Webhook endpoint is working  
✅ Message parsing is correct  
✅ Trace creation is working  
✅ Agent routing is configured  

---

## Test 8: Check Message Traces

### Purpose
Retrieve the message trace to see the complete processing flow.

### Postman Request

**Method:** `GET`

**URL:**
```
http://localhost:8882/api/v1/traces
```

**Headers:**
```
x-api-key: omni-dev-key-test-2025
```

**Query Parameters:**
```
instance_name = whatsapp-bot
page = 1
page_size = 10
```

### Step-by-Step in Postman

1. Create new tab
2. Method: `GET`
3. URL: `http://localhost:8882/api/v1/traces`
4. Click "Params" tab
5. Add parameters:
   ```
   Key: instance_name
   Value: whatsapp-bot
   
   Key: page
   Value: 1
   
   Key: page_size
   Value: 10
   ```
6. Headers:
   ```
   Key: x-api-key
   Value: omni-dev-key-test-2025
   ```
7. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
[
  {
    "trace_id": "ff1ff0da-c57b-429b-a378-d4a242a4ef29",
    "instance_name": "whatsapp-bot",
    "status": "completed",
    "message_type": "text",
    "message_content": "Hello Omni! Can you echo this back?",
    "sender_phone": "919014456421",
    "sender_name": "Vignesh",
    "agent_processing_time_ms": 1234,
    "total_processing_time_ms": 2500,
    "agent_response_success": true,
    "evolution_success": true,
    "created_at": "2025-12-12T10:30:05.123456"
  }
]
```

### What This Tests

✅ Message was processed successfully  
✅ Agent received and responded to message  
✅ Complete flow from webhook to response  
✅ Trace recording is working  

### Trace Status Meanings

| Status | Meaning |
|--------|---------|
| `processing` | Message currently being processed |
| `completed` | Message processed successfully, response sent |
| `error` | Error occurred during processing |
| `webhook_received` | Initial stage |
| `agent_called` | Request sent to agent |

---

## Test 9: Get Single Trace Details

### Purpose
Get detailed information about a specific message trace.

### Postman Request

**Method:** `GET`

**URL:**
```
http://localhost:8882/api/v1/traces/ff1ff0da-c57b-429b-a378-d4a242a4ef29
```

**Headers:**
```
x-api-key: omni-dev-key-test-2025
```

**Body:** (None)

### Step-by-Step in Postman

1. Create new tab
2. Method: `GET`
3. URL: `http://localhost:8882/api/v1/traces/{trace_id}`
   - Replace `{trace_id}` with the trace_id from Test 8
4. Headers:
   ```
   Key: x-api-key
   Value: omni-dev-key-test-2025
   ```
5. Click "Send"

### Expected Response

**Status:** `200 OK`

```json
{
  "trace_id": "ff1ff0da-c57b-429b-a378-d4a242a4ef29",
  "instance_name": "whatsapp-bot",
  "status": "completed",
  "message_type": "text",
  "message_content": "Hello Omni! Can you echo this back?",
  "sender_phone": "919014456421",
  "sender_name": "Vignesh",
  "session_id": "session-abc123",
  "session_name": "whatsapp-bot_919014456421",
  
  "incoming_payload": {
    "event": "messages.upsert",
    "data": {
      "messages": [
        {
          "key": { "remoteJid": "919014456421@s.whatsapp.net" },
          "message": { "conversation": "Hello Omni! Can you echo this back?" }
        }
      ]
    }
  },
  
  "agent_request_payload": {
    "user_id": "a3e4f8c9-d2b1-5e6f-7a8b-9c0d1e2f3a4b",
    "session_id": "session-abc123",
    "message": "Hello Omni! Can you echo this back?",
    "message_type": "text",
    "session_origin": "whatsapp"
  },
  
  "agent_response_payload": {
    "text": "Echo: Hello Omni! Can you echo this back?",
    "success": true,
    "session_id": "session-abc123"
  },
  
  "outgoing_payload": {
    "number": "919014456421",
    "text": "Echo: Hello Omni! Can you echo this back?",
    "instance": "whatsapp-bot"
  },
  
  "agent_processing_time_ms": 1234,
  "total_processing_time_ms": 2500,
  "agent_response_success": true,
  "evolution_success": true,
  "created_at": "2025-12-12T10:30:05.123456"
}
```

### What This Tests

✅ Complete message lifecycle captured  
✅ All payloads recorded (incoming, agent, outgoing)  
✅ Performance metrics captured  
✅ Success status at each stage  

### Reading the Trace

```
1. incoming_payload     → What WhatsApp sent
2. agent_request_payload → What Omni sent to agent
3. agent_response_payload → What agent returned
4. outgoing_payload     → What would be sent back to WhatsApp
5. Times & Success      → Performance and status
```

---

## Test 10: Complete End-to-End Message Flow

### Purpose
Test the entire flow: Message → Omni → Agent → Response → Trace

### Steps to Perform

**Step 1: Send Message to Webhook**
- Use Test 7
- Record the `trace_id` from response

**Step 2: Wait 2 Seconds**
- Allows processing time

**Step 3: Get Trace Details**
- Use Test 9 with the `trace_id` from Step 1

**Step 4: Verify Flow**
- Check that all payloads are present
- Check that `status` is "completed"
- Check that `agent_response_success` is true

### Success Criteria

✅ Webhook returns `200 OK` (message received)  
✅ Trace shows `status: "completed"`  
✅ `agent_response_success: true` (agent processed)  
✅ All payloads present (incoming, agent_request, agent_response, outgoing)  
✅ `total_processing_time_ms` is reasonable (<5000ms)  

### If Something Fails

**Webhook returns 400:**
- Check message JSON format
- Ensure `messages` is an array
- Check `remoteJid` format

**Trace shows `status: "error"`:**
- Check `error_message` field
- Agent URL might be wrong
- Agent might not be running

**Agent processing time very high (>10000ms):**
- Agent might be overloaded
- Network latency issue
- Increase `agent_timeout` if needed

---

## Test 11: Discord Instance Setup

### Purpose
Create a Discord bot instance (optional).

### Prerequisites

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Go to "Bot" tab → "Add Bot"
4. Copy the token
5. Enable these intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Direct Messages Intent
6. Go to OAuth2 → URL Generator
7. Select scopes: `bot`
8. Select permissions: `Send Messages`, `Read Messages`, `Manage Messages`
9. Copy generated URL and invite bot to your server

### Postman Request

**Method:** `POST`

**URL:**
```
http://localhost:8882/api/v1/instances
```

**Headers:**
```
Content-Type: application/json
x-api-key: omni-dev-key-test-2025
```

**Body (Raw JSON):**
```json
{
  "name": "discord-bot",
  "channel_type": "discord",
  "discord_bot_token": "YOUR_DISCORD_BOT_TOKEN_HERE",
  "discord_client_id": "YOUR_CLIENT_ID_HERE",
  "discord_guild_id": "YOUR_GUILD_ID_HERE",
  "discord_default_channel_id": "YOUR_CHANNEL_ID_HERE",
  "discord_voice_enabled": true,
  "discord_slash_commands_enabled": true,
  "agent_api_url": "http://localhost:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "agent_timeout": 60
}
```

### Expected Response

**Status:** `201 Created`

```json
{
  "id": 2,
  "name": "discord-bot",
  "channel_type": "discord",
  "discord_bot_token": "***",
  "discord_client_id": "123456789",
  "discord_guild_id": "987654321",
  "agent_api_url": "http://localhost:8886",
  "is_active": true,
  "created_at": "2025-12-12T11:00:00.123456"
}
```

### Test Discord Bot

1. Mention the bot in your Discord server
2. Send message: `@BotName Hello`
3. Bot should respond with: `Echo: Hello`

---

## Troubleshooting

### Issue: 401 Unauthorized

**Symptoms:**
```
{
  "detail": "Invalid API key"
}
```

**Solution:**
- Check `x-api-key` header is present
- Verify value: `omni-dev-key-test-2025`
- Make sure it's spelled exactly

---

### Issue: Connection Refused

**Symptoms:**
```
Error: connect ECONNREFUSED 127.0.0.1:8882
```

**Solution:**
- Check Omni API is running: `python -m src.api.app`
- Check port 8882 is available
- Try: `curl http://localhost:8882/health`

---

### Issue: Webhook Returns 400

**Symptoms:**
```
{
  "detail": "Invalid request format"
}
```

**Solution:**
- Check JSON is valid (use online JSON validator)
- Ensure `messages` is an array
- Check all required fields present
- Fix indentation and quotes

---

### Issue: No Response from Agent

**Symptoms:**
- Webhook returns 200
- Trace shows `status: "agent_called"`
- `agent_response_success: false`

**Solution:**
- Check agent is running: `python agent-echo.py`
- Check agent URL in instance config
- Try accessing `http://localhost:8886/health` directly
- Check agent logs for errors

---

### Issue: Evolution Key Error

**Symptoms:**
```
"error": "401 Unauthorized"
```

**Solution:**
- Get correct key from Evolution API manager
- Update instance: `PUT /api/v1/instances/whatsapp-bot`
- Check evolution_url is correct
- Ensure key is not expired

---

## Quick Reference

### URLs

```
Omni API Base:        http://localhost:8882
Echo Agent:           http://localhost:8886
Health checks:        GET /health (add to both base URLs)
Create instance:      POST /api/v1/instances
List instances:       GET /api/v1/instances
Get instance:         GET /api/v1/instances/{name}
QR code:             GET /api/v1/instances/{name}/qr
Send webhook:        POST /webhook/evolution/{name}
List traces:         GET /api/v1/traces
Get trace:           GET /api/v1/traces/{trace_id}
```

### Headers (Always Include)

```
Content-Type: application/json
x-api-key: omni-dev-key-test-2025  (for authenticated endpoints)
```

### Common Payloads

**WhatsApp Message:**
```json
{
  "event": "messages.upsert",
  "data": {
    "messages": [{
      "key": { "remoteJid": "919014456421@s.whatsapp.net", "id": "test" },
      "message": { "conversation": "Hello" },
      "messageTimestamp": 1702390000,
      "pushName": "Vignesh"
    }]
  }
}
```

**Create Instance:**
```json
{
  "name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "YOUR_KEY",
  "whatsapp_instance": "whatsapp-bot",
  "agent_api_url": "http://localhost:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo"
}
```

---

## Testing Checklist

- [ ] Test 1: Echo Agent Health ✅
- [ ] Test 2: Omni API Health ✅
- [ ] Test 3: Create Instance ✅
- [ ] Test 4: List Instances ✅
- [ ] Test 5: Get Instance Details ✅
- [ ] Test 6: Get QR Code ✅
- [ ] Test 7: Send Webhook Message ✅
- [ ] Test 8: List Traces ✅
- [ ] Test 9: Get Trace Details ✅
- [ ] Test 10: End-to-End Flow ✅
- [ ] Test 11: Discord Setup (Optional) ✅

---

**All tests passing? 🎉 System is ready for production!**

