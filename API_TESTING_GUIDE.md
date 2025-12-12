# Automagic Omni - Complete API Testing Guide

**Date:** December 11, 2025  
**Version:** 1.0  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Environment Setup](#environment-setup)
4. [API Endpoints](#api-endpoints)
   - [Instance Management](#instance-management)
   - [Webhook Endpoints](#webhook-endpoints)
   - [Trace & Monitoring](#trace--monitoring)
   - [Agent API](#agent-api)
5. [Testing Procedures](#testing-procedures)
6. [Postman Collection Setup](#postman-collection-setup)

---

## Overview

**Automagic Omni** is a multi-tenant WhatsApp message routing and processing system that:
- Receives WhatsApp messages via Evolution API webhook
- Routes messages to an AI agent for processing
- Returns responses back to WhatsApp users
- Maintains detailed audit trails of all messages

### Key Components

| Component | Port | Purpose |
|-----------|------|---------|
| **Omni API** | 8882 | Main webhook receiver & instance management |
| **Echo Agent** | 8886 | AI agent for message processing |
| **Evolution API** | External | WhatsApp gateway (cloud-hosted) |

---

## Architecture

```
WhatsApp Message
        ↓
Evolution API (receives from WhatsApp)
        ↓
Omni Webhook Endpoint (port 8882)
        ↓
Message Router (routes to agent)
        ↓
Echo Agent API (port 8886)
        ↓
Response Processor
        ↓
Evolution API (sends to WhatsApp)
        ↓
WhatsApp User (receives response)
```

---

## Environment Setup

### Prerequisites

- Python 3.8+
- Postman (for API testing)
- Omni API running: `python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8882`
- Echo Agent running: `python agent-echo.py`

### Base URLs

```
Omni API:      http://localhost:8882
Agent API:     http://localhost:8886
Evolution API: https://evolution-api-production-7611.up.railway.app
```

### Authentication

```
Omni API Key: omni-dev-key-test-2025
Evolution API Key: FA758317-709D-4BB6-BA4F-987B2335036A
```

---

# API ENDPOINTS

---

## INSTANCE MANAGEMENT

### 1. Create Instance

**Purpose:** Create a new WhatsApp instance configuration in Omni

**When to use:**
- Setting up a new WhatsApp bot/integration
- Creating separate instances for different use cases
- Multi-tenant deployment

**Endpoint:**
```
POST /api/v1/instances
```

**URL:**
```
http://localhost:8882/api/v1/instances
```

**Headers:**
```json
{
  "Content-Type": "application/json",
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Request Body:**
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
  "is_default": false
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "FA758317-709D-4BB6-BA4F-987B2335036A",
  "whatsapp_instance": "whatsapp-bot",
  "session_id_prefix": "whatsapp-bot-",
  "webhook_base64": true,
  "agent_api_url": "http://172.16.141.205:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "agent_timeout": 60,
  "is_default": false,
  "is_active": true,
  "created_at": "2025-12-10T14:53:04.062339",
  "updated_at": "2025-12-10T15:04:33.387695"
}
```

**Key Fields Explained:**

| Field | Purpose | Example |
|-------|---------|---------|
| `name` | Unique instance identifier | `whatsapp-bot` |
| `evolution_url` | WhatsApp API gateway URL | `https://evolution-api-production-7611.up.railway.app` |
| `evolution_key` | API key for Evolution API authentication | `FA758317-709D-4BB6-BA4F-987B2335036A` |
| `whatsapp_instance` | Instance name in Evolution API | `whatsapp-bot` |
| `agent_api_url` | URL to AI agent service | `http://localhost:8886` |
| `agent_api_key` | Authentication key for agent | `echo-test-key` |
| `default_agent` | Default agent to use | `echo` |
| `agent_timeout` | Timeout in seconds for agent responses | `60` |
| `webhook_base64` | Whether webhook sends base64-encoded payloads | `true` |

**Postman Test:**

1. **Create New Request**
   - Method: `POST`
   - URL: `http://localhost:8882/api/v1/instances`

2. **Add Headers**
   - Key: `Content-Type` → Value: `application/json`
   - Key: `x-api-key` → Value: `omni-dev-key-test-2025`

3. **Add Body (raw JSON)**
   - Copy the Request Body from above

4. **Click Send**
   - Expected: Status `201 Created`

---

### 2. Get All Instances

**Purpose:** Retrieve list of all configured instances

**Endpoint:**
```
GET /api/v1/instances
```

**URL:**
```
http://localhost:8882/api/v1/instances
```

**Headers:**
```json
{
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "whatsapp-test",
    "channel_type": "whatsapp",
    "agent_api_url": "http://172.16.141.205:8886",
    "agent_api_key": "echo-agent-key",
    "is_active": false
  },
  {
    "id": 2,
    "name": "whatsapp-bot",
    "channel_type": "whatsapp",
    "agent_api_url": "http://172.16.141.205:8886",
    "agent_api_key": "echo-test-key",
    "is_active": true
  }
]
```

**Postman Test:**

1. Method: `GET`
2. URL: `http://localhost:8882/api/v1/instances`
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Click Send → Status `200 OK`

---

### 3. Get Single Instance

**Purpose:** Retrieve details of a specific instance

**Endpoint:**
```
GET /api/v1/instances/{instance_name}
```

**URL:**
```
http://localhost:8882/api/v1/instances/whatsapp-bot
```

**Headers:**
```json
{
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "FA758317-709D-4BB6-BA4F-987B2335036A",
  "whatsapp_instance": "whatsapp-bot",
  "session_id_prefix": "whatsapp-bot-",
  "webhook_base64": true,
  "agent_api_url": "http://172.16.141.205:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "agent_timeout": 60,
  "is_default": false,
  "is_active": true,
  "enable_auto_split": true,
  "profile_name": "Omni Bot",
  "profile_pic_url": "https://...",
  "owner_jid": "919014456421@s.whatsapp.net",
  "created_at": "2025-12-10T14:53:04.062339",
  "updated_at": "2025-12-10T15:04:33.387695",
  "evolution_status": {
    "state": "open",
    "owner_jid": "919014456421@s.whatsapp.net",
    "profile_name": "Omni Bot",
    "last_updated": "2025-12-11T10:30:00.000000"
  }
}
```

**Postman Test:**

1. Method: `GET`
2. URL: `http://localhost:8882/api/v1/instances/whatsapp-bot`
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Click Send

---

### 4. Update Instance

**Purpose:** Update configuration of an existing instance

**When to use:**
- Change agent API endpoint
- Update agent timeout
- Modify Evolution API credentials
- Change default agent

**Endpoint:**
```
PUT /api/v1/instances/{instance_name}
```

**URL:**
```
http://localhost:8882/api/v1/instances/whatsapp-bot
```

**Headers:**
```json
{
  "Content-Type": "application/json",
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Request Body (only include fields to update):**
```json
{
  "agent_api_url": "http://localhost:8886",
  "agent_timeout": 90,
  "default_agent": "echo"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "whatsapp-bot",
  "agent_api_url": "http://172.16.141.205:8886",
  "agent_timeout": 90,
  "default_agent": "echo",
  "updated_at": "2025-12-11T10:35:00.000000"
}
```

**Postman Test:**

1. Method: `PUT`
2. URL: `http://localhost:8882/api/v1/instances/whatsapp-bot`
3. Headers: Add `x-api-key: omni-dev-key-test-2025`
4. Body (raw JSON): Include fields to update
5. Click Send

---

### 5. Delete Instance

**Purpose:** Remove an instance configuration

**When to use:**
- Decommission an old bot
- Clean up test instances
- Remove inactive integrations

**Endpoint:**
```
DELETE /api/v1/instances/{instance_name}
```

**URL:**
```
http://localhost:8882/api/v1/instances/whatsapp-bot
```

**Headers:**
```json
{
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Response (200 OK):**
```json
{
  "message": "Instance whatsapp-bot deleted successfully",
  "deleted_id": 2
}
```

**Postman Test:**

1. Method: `DELETE`
2. URL: `http://localhost:8882/api/v1/instances/whatsapp-bot`
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Click Send → Status `200 OK`

---

## WEBHOOK ENDPOINTS

### 1. WhatsApp Message Webhook (Evolution API)

**Purpose:** Receive messages from WhatsApp via Evolution API

**When to use:**
- Automatically triggered when WhatsApp message arrives
- Can be triggered manually for testing

**Endpoint:**
```
POST /webhook/evolution/{instance_name}
```

**URL:**
```
http://localhost:8882/webhook/evolution/whatsapp-bot
```

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Request Body (Option 1: Raw JSON - Recommended for Testing)**
```json
{
  "key": {
    "remoteJid": "919391189719@s.whatsapp.net",
    "fromMe": false,
    "id": "test_msg_001"
  },
  "messageTimestamp": 1765375800,
  "pushName": "Pavan",
  "status": "PENDING",
  "message": {
    "conversation": "Hello! This is a test message from Postman."
  }
}
```

**Request Body (Option 2: Base64-Encoded - Evolution API Format)**
```json
{
  "data": "eyJrZXkiOnsicmVtb3RlSmlkIjoiOTE5MzkxMTg5NzE5QHMud2hhdHNhcHAubmV0IiwiZnJvbU1lIjpmYWxzZSwiaWQiOiJ0ZXN0X21zZ18wMDEifSwibWVzc2FnZVRpbWVzdGFtcCI6MTc2NTM3NTgwMCwicHVzaE5hbWUiOiJQYXZhbiIsInN0YXR1cyI6IlBFTkRJTkciLCJtZXNzYWdlIjp7ImNvbnZlcnNhdGlvbiI6IkhlbGxvISBUaGlzIGlzIGEgdGVzdCBtZXNzYWdlIGZyb20gUG9zdG1hbi4ifX0="
}
```

**Response (200 OK):**
```json
{
  "trace_id": "f86e4bc9-14b4-425f-9a3a-d6c027f8ff90",
  "status": "received",
  "message": "Message received and queued for processing"
}
```

**What Happens After Webhook Receives Message:**

1. **Message is extracted** from payload
2. **Trace is created** (unique ID for tracking)
3. **Message is queued** for async processing
4. **Webhook returns 200** immediately
5. **Background process**:
   - Routes to agent API
   - Agent generates response
   - Response sent to Evolution API
   - WhatsApp user receives message

**Postman Test:**

1. Method: `POST`
2. URL: `http://localhost:8882/webhook/evolution/whatsapp-bot`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Copy "Option 1" from above
5. Click Send → Status `200 OK`
6. Copy `trace_id` from response
7. Use trace_id to check processing status (see Trace endpoint)

**Field Definitions:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `remoteJid` | string | Sender's WhatsApp ID | `919391189719@s.whatsapp.net` |
| `fromMe` | boolean | Whether message is from bot | `false` |
| `id` | string | Unique message ID | `test_msg_001` |
| `messageTimestamp` | integer | Unix timestamp | `1765375800` |
| `pushName` | string | Sender's display name | `Pavan` |
| `status` | string | Message status | `PENDING` |
| `conversation` | string | Message text content | `Hello!...` |

---

## TRACE & MONITORING

### 1. Get All Traces

**Purpose:** View all message processing traces/audit logs

**When to use:**
- Debugging message flow
- Monitoring system health
- Auditing message processing

**Endpoint:**
```
GET /api/v1/traces
```

**URL:**
```
http://localhost:8882/api/v1/traces
```

**Headers:**
```json
{
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Query Parameters (Optional):**
```
?limit=50&offset=0&status=completed&instance=whatsapp-bot
```

**Response (200 OK):**
```json
[
  {
    "id": "f86e4bc9-14b4-425f-9a3a-d6c027f8ff90",
    "instance_name": "whatsapp-bot",
    "phone_number": "919391189719",
    "status": "completed",
    "message_text": "Hello! This is a test message from Postman.",
    "agent_response": "[Echo from whatsapp] [Pavan]: Hello! This is a test message from Postman.",
    "evolution_success": true,
    "created_at": "2025-12-11T10:42:30.000000",
    "completed_at": "2025-12-11T10:42:32.500000",
    "processing_time_ms": 2500
  }
]
```

**Trace Status Values:**

| Status | Meaning | Action Taken |
|--------|---------|--------------|
| `received` | Webhook just received message | ⏳ Waiting to queue |
| `processing` | Message queued, awaiting processing | ⏳ Processing |
| `agent_called` | Agent API called | ⏳ Waiting for agent response |
| `completed` | Message fully processed, response sent | ✅ Success |
| `failed` | Error during processing | ❌ Check logs |

**Postman Test:**

1. Method: `GET`
2. URL: `http://localhost:8882/api/v1/traces`
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Click Send
5. Look for traces with `status: completed`

---

### 2. Get Single Trace

**Purpose:** View detailed information about a specific message

**When to use:**
- Debugging a specific message
- Checking if message was sent to WhatsApp
- Verifying agent response

**Endpoint:**
```
GET /api/v1/traces/{trace_id}
```

**URL:**
```
http://localhost:8882/api/v1/traces/f86e4bc9-14b4-425f-9a3a-d6c027f8ff90
```

**Headers:**
```json
{
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Response (200 OK):**
```json
{
  "id": "f86e4bc9-14b4-425f-9a3a-d6c027f8ff90",
  "instance_name": "whatsapp-bot",
  "phone_number": "919391189719",
  "contact_name": "Pavan",
  "message_id": "test_pavan_1765375800",
  "status": "completed",
  "message_text": "Hello! This is a test message from Postman.",
  "agent_name": "echo",
  "agent_response": "[Echo from whatsapp] [Pavan]: Hello! This is a test message from Postman.",
  "evolution_response_status": 201,
  "evolution_success": true,
  "created_at": "2025-12-11T10:42:30.000000",
  "completed_at": "2025-12-11T10:42:32.500000",
  "processing_time_ms": 2500,
  "webhooks": {
    "received_at": "2025-12-11T10:42:30.000000",
    "agent_called_at": "2025-12-11T10:42:30.100000",
    "response_sent_at": "2025-12-11T10:42:32.500000"
  }
}
```

**Postman Test:**

1. Method: `GET`
2. URL: `http://localhost:8882/api/v1/traces/f86e4bc9-14b4-425f-9a3a-d6c027f8ff90` (replace with your trace_id)
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Click Send

---

## AGENT API

### 1. Chat Endpoint (Echo Agent)

**Purpose:** Send a message to the AI agent and get a response

**When to use:**
- Direct testing of agent responses
- Debugging agent behavior
- Testing custom agent implementations

**Endpoint:**
```
POST /api/agent/chat
```

**URL:**
```
http://localhost:8886/api/agent/chat
```

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "user_id": "d3b657af-d006-5e44-915b-dd08353f1b38",
  "session_id": "2781b4f5-c907-559c-9967-cc296d2c1a0a",
  "session_name": "whatsapp-bot_919391189719",
  "message": "[Pavan]: Hello! This is a test message from Postman.",
  "message_type": "text",
  "session_origin": "whatsapp",
  "user": {
    "phone_number": "+919391189719",
    "email": null,
    "user_data": null
  }
}
```

**Response (200 OK):**
```json
{
  "text": "[Echo from whatsapp] [Pavan]: Hello! This is a test message from Postman.",
  "message": "[Echo from whatsapp] [Pavan]: Hello! This is a test message from Postman.",
  "success": true,
  "session_id": "unknown"
}
```

**Field Definitions:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `user_id` | string | Unique user identifier | UUID string |
| `session_id` | string | Session/conversation ID | UUID string |
| `session_name` | string | Human-readable session name | `whatsapp-bot_919391189719` |
| `message` | string | User's message | `Hello agent` |
| `message_type` | string | Type of message | `text`, `image`, `audio` |
| `session_origin` | string | Channel origin | `whatsapp`, `discord` |
| `user.phone_number` | string | User's phone number | `+919391189719` |

**Postman Test:**

1. Method: `POST`
2. URL: `http://localhost:8886/api/agent/chat`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Copy request body from above
5. Click Send → Status `200 OK`

---

### 2. Health Check Endpoint

**Purpose:** Verify agent API is running and healthy

**When to use:**
- Monitoring agent availability
- Debugging connection issues
- System health checks

**Endpoint:**
```
GET /health
```

**URL:**
```
http://localhost:8886/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "echo-agent"
}
```

**Postman Test:**

1. Method: `GET`
2. URL: `http://localhost:8886/health`
3. Click Send → Status `200 OK`

---

# TESTING PROCEDURES

---

## Complete End-to-End Test Flow

### Scenario: Test WhatsApp Message Processing

**Objective:** Send a message via webhook and verify it reaches WhatsApp

**Time Required:** 5 minutes

**Steps:**

1. **Verify Services Are Running**
   ```bash
   # Terminal 1: Omni API
   python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8882 --reload
   
   # Terminal 2: Echo Agent
   python agent-echo.py
   ```

2. **Check Agent API Health**
   - Method: GET
   - URL: `http://localhost:8886/health`
   - Expected: Status `200 OK`

3. **Retrieve Instances**
   - Method: GET
   - URL: `http://localhost:8882/api/v1/instances`
   - Headers: `x-api-key: omni-dev-key-test-2025`
   - Verify: `whatsapp-bot` instance exists

4. **Send Test Message via Webhook**
   - Method: POST
   - URL: `http://localhost:8882/webhook/evolution/whatsapp-bot`
   - Headers: `Content-Type: application/json`
   - Body:
   ```json
   {
     "key": {
       "remoteJid": "919391189719@s.whatsapp.net",
       "fromMe": false,
       "id": "test_001"
     },
     "messageTimestamp": 1765375800,
     "pushName": "Pavan",
     "status": "PENDING",
     "message": {
       "conversation": "Hello from Postman test!"
     }
   }
   ```
   - Expected: Status `200 OK` with `trace_id`

5. **Check Trace Status**
   - Method: GET
   - URL: `http://localhost:8882/api/v1/traces` (or use specific trace_id)
   - Headers: `x-api-key: omni-dev-key-test-2025`
   - Expected: Status `completed` with `evolution_success: true`

6. **Verify Agent Response**
   - Check trace details for `agent_response` field
   - Should contain echo message

**Expected Results:**

```
✅ Webhook Status: 200
✅ Trace Status: completed
✅ Evolution Success: true
✅ Message in Logs: "Sent response to 919391189719"
```

---

## Test Different Message Types

### Test 1: Simple Text Message

```json
{
  "key": {
    "remoteJid": "919391189719@s.whatsapp.net",
    "fromMe": false,
    "id": "test_text_001"
  },
  "messageTimestamp": 1765375800,
  "pushName": "Pavan",
  "status": "PENDING",
  "message": {
    "conversation": "Hi, how are you?"
  }
}
```

---

### Test 2: Message from Different User

```json
{
  "key": {
    "remoteJid": "917396804318@s.whatsapp.net",
    "fromMe": false,
    "id": "test_balaji_001"
  },
  "messageTimestamp": 1765375800,
  "pushName": "Balaji",
  "status": "PENDING",
  "message": {
    "conversation": "Testing from different user"
  }
}
```

---

### Test 3: Long Message

```json
{
  "key": {
    "remoteJid": "919391189719@s.whatsapp.net",
    "fromMe": false,
    "id": "test_long_001"
  },
  "messageTimestamp": 1765375800,
  "pushName": "Pavan",
  "status": "PENDING",
  "message": {
    "conversation": "This is a longer test message with multiple sentences. It should be properly processed by the agent and returned as an echo response. Let's verify that the entire message is captured and processed correctly."
  }
}
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Webhook returns 404** | Instance name doesn't exist | Verify instance with GET `/api/v1/instances` |
| **Trace status stuck at "agent_called"** | Agent API timeout | Check agent is running on port 8886 |
| **Evolution Success: false** | Agent URL not reachable | Verify IP address conversion in instance config |
| **No trace created** | Message parsing error | Check JSON format, verify `remoteJid` field |
| **Agent returns timeout error** | Agent processing slow | Increase `agent_timeout` in instance config |

---

# POSTMAN COLLECTION SETUP

---

## Create Postman Collection

### Step 1: Create Environment

1. Open Postman
2. Click **Environments** (left sidebar)
3. Click **+** to create new environment
4. Name: `Omni-Dev`
5. Add Variables:

```
OMNI_URL:        http://localhost:8882
AGENT_URL:       http://localhost:8886
OMNI_API_KEY:    omni-dev-key-test-2025
TRACE_ID:        (will fill after webhook test)
INSTANCE_NAME:   whatsapp-bot
PHONE_NUMBER:    919391189719
```

6. Click **Save**

---

### Step 2: Create Collection

1. Click **Collections** (left sidebar)
2. Click **+** to create new collection
3. Name: `Omni WhatsApp API`
4. Add Requests (see below)

---

### Step 3: Add Requests to Collection

#### Request 1: Health Check - Agent API

```
Name: Health Check - Agent
Method: GET
URL: {{AGENT_URL}}/health
Headers: (none required)
```

---

#### Request 2: Get All Instances

```
Name: Get All Instances
Method: GET
URL: {{OMNI_URL}}/api/v1/instances
Headers:
  x-api-key: {{OMNI_API_KEY}}
```

---

#### Request 3: Get Single Instance

```
Name: Get Single Instance
Method: GET
URL: {{OMNI_URL}}/api/v1/instances/{{INSTANCE_NAME}}
Headers:
  x-api-key: {{OMNI_API_KEY}}
```

---

#### Request 4: Send Webhook Message

```
Name: Send Test Message via Webhook
Method: POST
URL: {{OMNI_URL}}/webhook/evolution/{{INSTANCE_NAME}}
Headers:
  Content-Type: application/json
Body:
{
  "key": {
    "remoteJid": "{{PHONE_NUMBER}}@s.whatsapp.net",
    "fromMe": false,
    "id": "postman_test_001"
  },
  "messageTimestamp": 1765375800,
  "pushName": "Test User",
  "status": "PENDING",
  "message": {
    "conversation": "Hello from Postman!"
  }
}
```

**Post-request Script** (to save trace_id):
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("TRACE_ID", jsonData.trace_id);
    console.log("Trace ID: " + jsonData.trace_id);
}
```

---

#### Request 5: Get All Traces

```
Name: Get All Traces
Method: GET
URL: {{OMNI_URL}}/api/v1/traces
Headers:
  x-api-key: {{OMNI_API_KEY}}
```

---

#### Request 6: Get Single Trace

```
Name: Get Trace Details
Method: GET
URL: {{OMNI_URL}}/api/v1/traces/{{TRACE_ID}}
Headers:
  x-api-key: {{OMNI_API_KEY}}
```

---

#### Request 7: Send to Agent API

```
Name: Send Message to Agent
Method: POST
URL: {{AGENT_URL}}/api/agent/chat
Headers:
  Content-Type: application/json
Body:
{
  "user_id": "test-user-123",
  "session_id": "test-session-123",
  "session_name": "whatsapp-bot_{{PHONE_NUMBER}}",
  "message": "Hello agent! Testing direct message.",
  "message_type": "text",
  "session_origin": "whatsapp",
  "user": {
    "phone_number": "+{{PHONE_NUMBER}}",
    "email": null,
    "user_data": null
  }
}
```

---

## Test Execution Order

1. **Health Check - Agent API** → Verify agent is running
2. **Get All Instances** → Verify whatsapp-bot exists
3. **Get Single Instance** → Verify configuration
4. **Send Test Message via Webhook** → Trigger message processing
5. **Get All Traces** → Monitor trace status
6. **Get Trace Details** → Verify completion and response
7. **Send to Agent API** → Test agent directly

---

## Expected Flow

```
┌─────────────────────────────────────┐
│ 1. Health Check (200 OK)            │
│    ✅ Agent is running              │
└──────────────┬──────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 2. Get Instances (200 OK)            │
│    ✅ whatsapp-bot found            │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 3. Send Webhook (200 OK + trace_id) │
│    ✅ Message queued                │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 4. Check Traces (status: completed)  │
│    ✅ evolution_success: true       │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 5. Get Trace Details (full response) │
│    ✅ Message sent to WhatsApp      │
└──────────────────────────────────────┘
```

---

## Troubleshooting Guide

### Agent API Not Responding

**Check:**
```bash
# Terminal
python agent-echo.py

# Postman
GET http://localhost:8886/health
```

**Solution:**
- Kill existing Python process: `Get-Process python | Stop-Process`
- Restart agent: `python agent-echo.py`

---

### Omni API Not Responding

**Check:**
```bash
# Terminal
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8882 --reload

# Postman
GET http://localhost:8882/api/v1/instances (with x-api-key header)
```

**Solution:**
- Check port 8882 is not in use: `netstat -ano | findstr :8882`
- Restart Omni: Kill and restart uvicorn

---

### Webhook Returns 404

**Check:**
- Instance name in URL matches exactly
- Instance exists: `GET /api/v1/instances`

**Solution:**
- Create instance if missing: `POST /api/v1/instances`
- Verify instance name spelling

---

### Trace Status Stuck at "agent_called"

**Check:**
- Agent API is running: `GET /health`
- Agent API URL in instance config is correct

**Solution:**
- Check logs for timeout errors
- Increase `agent_timeout` in instance config
- Verify agent can be reached from Omni

---

## Performance Metrics

| Metric | Expected | Units |
|--------|----------|-------|
| Webhook Response Time | < 100 | ms |
| Agent Response Time | 100-500 | ms |
| Total End-to-End Time | 1-3 | seconds |
| Trace Status Update | Real-time | - |

---

## Summary

You now have:
- ✅ Complete API documentation
- ✅ Step-by-step testing procedures
- ✅ Postman collection setup
- ✅ Common issues & solutions
- ✅ Performance benchmarks

**All systems are production-ready!** 🎉

