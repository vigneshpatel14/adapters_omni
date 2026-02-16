# COMPLETE TESTING GUIDE: Automagic Omni ↔ Leo Streaming Agent Integration

**Last Updated:** December 15, 2025  
**Status:** Production Ready  
**Version:** 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites & Environment](#prerequisites--environment)
3. [End-to-End System Flow](#end-to-end-system-flow)
4. [Complete Example Walkthrough](#complete-example-walkthrough)
5. [Test Scenarios](#test-scenarios)
6. [API Request/Response Reference](#api-requestresponse-reference)
7. [Manual Testing (curl/Postman)](#manual-testing-curlpostman)
8. [WhatsApp End-to-End Testing](#whatsapp-end-to-end-testing)
9. [Automated Testing Scripts](#automated-testing-scripts)
10. [Debugging & Traceability](#debugging--traceability)
11. [Troubleshooting Guide](#troubleshooting-guide)

---

## Overview

This guide provides comprehensive testing procedures for the Automagic Omni ↔ Leo streaming agent integration. It covers:
- **Complete request/response flows** with actual payloads
- **Step-by-step end-to-end example** showing a message from WhatsApp through Leo and back
- **All API calls** involved in the flow
- **Manual and automated testing** approaches
- **Debugging techniques** and log analysis
- **Troubleshooting common issues**

### System Architecture

```
┌─────────────┐
│   WhatsApp  │
│    User     │
└──────┬──────┘
       │ Sends: "What can you do?"
       ▼
┌──────────────────────────────────────┐
│  Evolution API (WhatsApp Gateway)    │
│  - Receives message from user        │
│  - Forwards via webhook              │
└──────┬───────────────────────────────┘
       │ POST /webhook/{instance}
       ▼
┌──────────────────────────────────────┐
│  Automagic Omni API (Port 8882)      │
│  - Receives webhook request          │
│  - Routes to adapter service         │
│  - Returns to user via Evolution API │
└──────┬───────────────────────────────┘
       │ POST /api/agent/chat
       ▼
┌──────────────────────────────────────┐
│  Leo Adapter Service (Port 8887)     │
│  - Translates Omni format → Leo      │
│  - Calls Leo streaming API           │
│  - Parses SSE response               │
│  - Translates Leo → Omni format      │
└──────┬───────────────────────────────┘
       │ POST /stream (with Bearer token)
       ▼
┌──────────────────────────────────────┐
│  Leo Streaming API (Remote)          │
│  - Processes message                 │
│  - Returns SSE stream with deltas    │
│  - Includes TEXT_MESSAGE_CONTENT     │
└──────┬───────────────────────────────┘
       │ SSE Response (streaming)
       ▼
[Response flows back through same path]
```

---

## Prerequisites & Environment

### Services Required (All Running)

```
Terminal 2: Omni API
$ python -m src
✅ Running on http://0.0.0.0:8882


### Configuration Files Required

1. **`.env.leo`** - Leo adapter configuration
```env
LEO_BEARER_TOKEN=eyJhbGciOiJIUzI1NiIs...  # From browser DevTools
LEO_WORKFLOW_ID=e9f65742-8f61-4a7f-b0d2-71b77c5391e7
LEO_API_BASE_URL=https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1
LEO_SUBSCRIPTION_KEY=018ca54b...
ADAPTER_API_KEY=leo-adapter-key-2025
ADAPTER_PORT=8887
```

2. **Instance Configuration in Omni**
- Instance name: `whatsapp-leo-bot`
- Agent API URL: `http://localhost:8887`
- Agent API Key: `leo-adapter-key-2025`
- Agent timeout: `120` seconds

### Validation Checklist
- [ ] Leo adapter health: `GET http://localhost:8887/health` → 200 OK
- [ ] Omni health: `GET http://localhost:8882/health` → 200 OK
- [ ] Leo bearer token is valid (not expired)
- [ ] Instance `whatsapp-leo-bot` exists in Omni
- [ ] WhatsApp number is registered in Evolution API

---

## End-to-End System Flow

### Message Journey (Step-by-Step)

**Phase 1: User Message Sent**
```
1. User sends WhatsApp message: "What can you do?"
   ↓
2. Evolution API receives message from WhatsApp
   ↓
3. Evolution API triggers webhook to Omni
```

**Phase 2: Omni Processing**
```
4. Omni receives POST /webhook/evolution/whatsapp-leo-bot
   - Parses message content
   - Creates message trace record (status: pending)
   - Looks up instance config
   - Validates access control (allowed users)
   ↓
5. Omni calls agent via POST /api/agent/chat
   - Sends request to Leo adapter
   - Includes user_id, message content, session context
```

**Phase 3: Leo Adapter Processing**
```
6. Adapter receives request at /api/agent/chat
   - Validates API key (leo-adapter-key-2025)
   - Translates Omni format → Leo format
   ↓
7. Adapter calls Leo streaming API
   - Sends user_id, message, auth headers
   - Receives SSE stream with TEXT_MESSAGE_CONTENT deltas
   ↓
8. Adapter parses Leo SSE response
   - Concatenates deltas: "What can I do?"
   - Extracts final response text
   - Translates Leo format → Omni format
```

**Phase 4: Response Back to User**
```
9. Adapter returns response to Omni
   - Status: 200 OK
   - Body: {"text": "Leo's response..."}
   ↓
10. Omni processes response
    - Updates message trace (status: completed)
    - Calls Evolution API to send response
    ↓
11. Evolution API sends to WhatsApp
    ↓
12. User receives response in WhatsApp
```

---

## Complete Example Walkthrough

### Scenario: User asks "What can you do?"

#### STEP 1: User Sends WhatsApp Message
**What happens:** User opens WhatsApp, types message, hits send
```
User Phone: +1 (555) 123-4567
Message: "What can you do?"
Time: 2025-12-15T14:32:00Z
```

#### STEP 2: Evolution API Webhook Triggered
**What Evolution API does:** Detects message, forwards to Omni webhook

**Evolution API Webhook Request (Sent to Omni):**
```http
POST /webhook/evolution/whatsapp-leo-bot HTTP/1.1
Host: localhost:8882
Content-Type: application/json
Content-Length: 452

{
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "919391189719@s.whatsapp.net",
      "fromMe": false,
      "id": "test_pavan_postman_001"
    },
    "messageTimestamp": 1765375800,
    "pushName": "Pavan",
    "status": "PENDING",
    "message": {
      "conversation": "give me a java code to check greatest of 3 numbers "
    }
  }
}
```

**Evolution API Response from Omni:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 22

{"status": "received"}
```

#### STEP 3: Omni Receives & Processes Webhook
**File:** `src/api/app.py` - Webhook endpoint

**Omni receives request:**
```python
# Webhook handler processes the Evolution API message
POST /webhook/evolution/whatsapp-leo-bot
├─ Extract phone: +15551234567
├─ Extract message: "What can you do?"
├─ Create trace record (trace_id: abc123...)
├─ Validate access control (user allowed? ✓)
├─ Look up instance config (whatsapp-leo-bot)
└─ Call agent API service
```

**Omni Trace Created:**
```json
{
  "trace_id": "abc123def456ghi789",
  "instance_id": "whatsapp-leo-bot",
  "user_id": "whatsapp:+15551234567",
  "message_content": "What can you do?",
  "status": "pending",
  "created_at": "2025-12-15T14:32:01Z",
  "steps": []
}
```

#### STEP 4: Omni Calls Leo Adapter
**File:** `src/services/agent_api_client.py` - Agent API client

**Omni Request to Leo Adapter:**
```http
POST /api/agent/chat HTTP/1.1
Host: localhost:8887
Content-Type: application/json
X-API-Key: leo-adapter-key-2025
Content-Length: 285

{
  "user_id": "whatsapp:+15551234567",
  "session_id": "session-abc123",
  "message": "What can you do?",
  "context": {
    "channel": "whatsapp",
    "instance": "whatsapp-leo-bot",
    "source": "evolution-api"
  },
  "session_origin": "whatsapp"
}
```

#### STEP 5: Leo Adapter Processes Request
**File:** `adapter-leo-agent.py` - Main adapter

**Adapter processing:**
```python
# Receive request from Omni
request = {
  "user_id": "whatsapp:+15551234567",
  "message": "What can you do?",
  ...
}

# Translate to Leo format
leo_payload = {
  "user_id": "whatsapp:+15551234567",
  "message": "What can you do?",
  "workflow_id": "e9f65742-8f61-4a7f-b0d2-71b77c5391e7"
}

# Log the request
DEBUG: Received request from user: whatsapp:+15551234567
DEBUG: Message: What can you do?
DEBUG: Calling Leo API: https://api-leodev.gep.com/.../stream
```

#### STEP 6: Leo Adapter Calls Leo Streaming API
**File:** `adapter-leo-agent.py` - Leo API call

**Leo Adapter Request (to Leo API):**
```http
POST /leo-portal-agentic-runtime-node-api/v1/stream HTTP/1.1
Host: api-leodev.gep.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
X-Subscription-Key: 018ca54b...
Content-Length: 215

{
  "user_id": "whatsapp:+15551234567",
  "message": "What can you do?",
  "workflow_id": "e9f65742-8f61-4a7f-b0d2-71b77c5391e7"
}
```

#### STEP 7: Leo API Streams Response (SSE Format)
**Leo API Response (Streaming):**
```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Transfer-Encoding: chunked

event: RUN_STARTED
data: {"run_id": "run-789xyz", "status": "started"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": "I am Leo,", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " your", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " AI assistant.", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " I can help", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " you with", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " questions,", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " analysis,", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " coding,", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " and much more!", "type": "text"}

event: RUN_FINISHED
data: {"run_id": "run-789xyz", "status": "completed", "final_response": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!"}
```

#### STEP 8: Adapter Parses SSE Response
**Adapter Processing:**
```python
# Parse streaming response
collected_deltas = []
for event in sse_stream:
    if event.type == "TEXT_MESSAGE_CONTENT":
        delta = json.loads(event.data)["delta"]
        collected_deltas.append(delta)
        # collected_deltas now: ["I am Leo,", " your", " AI assistant.", ...]

# Concatenate all deltas
final_text = "".join(collected_deltas)
# Result: "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!"

# Log the parsed response
INFO: Extracted text from Leo API: "I am Leo, your AI assistant..."
DEBUG: Deltas concatenated (9 total deltas)
```

**Adapter saves to debug file:**
```
File: leo_raw_response_debug.txt
Content:
event: RUN_STARTED
data: {"run_id": "run-789xyz", "status": "started"}
...
[Full streaming response logged]
```

#### STEP 9: Leo Adapter Returns to Omni
**Leo Adapter Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 185

{
  "text": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!"
}
```

#### STEP 10: Omni Processes Agent Response
**Omni Service Processing:**
```python
# Receive response from adapter
response = {
  "text": "I am Leo, your AI assistant..."
}

# Update trace record
trace.steps.append({
  "step": "agent_response_received",
  "status": "success",
  "response_preview": "I am Leo, your AI assistant...",
  "timestamp": "2025-12-15T14:32:08Z"
})

# Call Evolution API to send back to WhatsApp
LOG: Sending response to Evolution API for +15551234567
```

#### STEP 11: Omni Calls Evolution API to Send Message
**Omni Request to Evolution API:**
```http
POST /message/sendText/whatsapp-leo-bot HTTP/1.1
Host: evolution-api-production-7611.up.railway.app
Content-Type: application/json
X-API-Key: FA758317-709D-4BB6-BA4F-987B2335036A
Content-Length: 320

{
  "number": "+15551234567",
  "text": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!",
  "delay": 100
}
```

**Evolution API Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "key": {
    "remoteJid": "+15551234567@s.whatsapp.net",
    "fromMe": true,
    "id": "3EB0CEEF54321CBA"
  },
  "messageTimestamp": 1734274328,
  "status": "PENDING"
}
```

#### STEP 12: WhatsApp Delivers Message
**User receives in WhatsApp:**
```
Bot: "I am Leo, your AI assistant. I can help you with 
     questions, analysis, coding, and much more!"
```

#### STEP 13: Omni Updates Trace (Complete)
**Final Trace Record:**
```json
{
  "trace_id": "abc123def456ghi789",
  "instance_id": "whatsapp-leo-bot",
  "user_id": "whatsapp:+15551234567",
  "message_content": "What can you do?",
  "response_content": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!",
  "status": "completed",
  "duration_ms": 7850,
  "created_at": "2025-12-15T14:32:01Z",
  "completed_at": "2025-12-15T14:32:08Z",
  "steps": [
    {
      "step": "webhook_received",
      "status": "success",
      "timestamp": "2025-12-15T14:32:01Z"
    },
    {
      "step": "instance_validated",
      "status": "success",
      "instance_name": "whatsapp-leo-bot",
      "timestamp": "2025-12-15T14:32:01Z"
    },
    {
      "step": "access_control_checked",
      "status": "success",
      "user_allowed": true,
      "timestamp": "2025-12-15T14:32:02Z"
    },
    {
      "step": "agent_called",
      "status": "success",
      "agent_url": "http://localhost:8887",
      "duration_ms": 7200,
      "timestamp": "2025-12-15T14:32:09Z"
    },
    {
      "step": "agent_response_received",
      "status": "success",
      "response_preview": "I am Leo, your AI assistant...",
      "timestamp": "2025-12-15T14:32:09Z"
    },
    {
      "step": "evolution_api_called",
      "status": "success",
      "message_sent": true,
      "timestamp": "2025-12-15T14:32:10Z"
    }
  ],
  "evolution_api_success": true
}
```

---

## Test Scenarios

### Scenario 1: Basic Leo Response
**Test:** Simple message, verify Leo responds correctly
```
Input:  "Hello"
Output: Leo's greeting response
Time:   ~5-8 seconds
```

### Scenario 2: Complex Query
**Test:** Ask a complex question
```
Input:  "How do I build a React component for a form?"
Output: Detailed technical response from Leo
Time:   ~8-12 seconds
```

### Scenario 3: Multiple Messages (Session)
**Test:** Send several messages in sequence
```
1. "What's your name?"
2. "Can you help with Python?"
3. "Show me a code example"

Verify: Session context maintained across messages
```

### Scenario 4: Error Handling
**Test:** Send with expired token
```
Expected: 401 Unauthorized, clear error message
```

### Scenario 5: Performance
**Test:** Measure response times
```
Measure:
- Webhook → Agent call: ~100ms
- Agent → Leo API: ~3000-5000ms (network + processing)
- Leo → Response back: ~2000-3000ms
- Total: ~5-8 seconds
```

---

## API Request/Response Reference

### Complete Request Format (Omni → Adapter)

```json
{
  "user_id": "whatsapp:+15551234567",
  "session_id": "session-abc123def456",
  "message": "What can you do?",
  "context": {
    "channel": "whatsapp",
    "instance": "whatsapp-leo-bot",
    "source": "evolution-api",
    "timestamp": "2025-12-15T14:32:00Z"
  },
  "session_origin": "whatsapp"
}
```

### Complete Response Format (Adapter → Omni)

```json
{
  "text": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!"
}
```

### Adapter → Leo API Request

```json
{
  "user_id": "whatsapp:+15551234567",
  "message": "What can you do?",
  "workflow_id": "e9f65742-8f61-4a7f-b0d2-71b77c5391e7",
  "context": {
    "session_id": "session-abc123"
  }
}
```

### Leo API → Adapter Response (SSE Stream)

```
event: RUN_STARTED
data: {"run_id": "...", "status": "started"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": "I am Leo,", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " your AI assistant.", "type": "text"}

event: RUN_FINISHED
data: {"run_id": "...", "status": "completed", "final_response": "..."}
```

---

## Manual Testing (curl/Postman)

### Test 1: Adapter Health Check

```bash
curl -X GET http://localhost:8887/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "leo_api_configured": true,
  "leo_api_reachable": true,
  "timestamp": "2025-12-15T14:30:00Z"
}
```

### Test 2: Direct Adapter Test (No Omni)

```bash
curl -X POST http://localhost:8887/api/agent/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: leo-adapter-key-2025" \
  -d '{
    "user_id": "test-user-123",
    "session_id": "test-session",
    "message": "What can you do?",
    "context": {
      "channel": "test",
      "source": "direct_test"
    },
    "session_origin": "test"
  }'
```

**Expected Response (200 OK):**
```json
{
  "text": "I am Leo, your AI assistant. I can help you with..."
}
```

### Test 3: Omni Instance Creation

```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "Content-Type: application/json" \
  -H "x-api-key: omni-dev-key-test-2025" \
  -d '{
    "name": "whatsapp-leo-bot",
    "evolution_url": "https://evolution-api-production-7611.up.railway.app",
    "evolution_key": "FA758317-709D-4BB6-BA4F-987B2335036A",
    "whatsapp_instance": "whatsapp-leo-bot",
    "agent_api_url": "http://localhost:8887",
    "agent_api_key": "leo-adapter-key-2025",
    "default_agent": "leo-adapter",
    "agent_timeout": 120,
    "webhook_base64": false,
    "is_active": true,
    "is_default": false,
    "auto_qr": true
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "name": "whatsapp-leo-bot",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "whatsapp_instance": "whatsapp-leo-bot",
  "agent_api_url": "http://localhost:8887",
  "agent_api_key": "leo-adapter-key-2025",
  "is_active": true,
  "created_at": "2025-12-15T14:30:00Z"
}
```

### Test 4: Get QR Code

```bash
curl -X GET http://localhost:8882/api/v1/instances/whatsapp-leo-bot/qr \
  -H "x-api-key: omni-dev-key-test-2025"
```

**Expected Response (200 OK):**
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMI...",
  "instance_name": "whatsapp-leo-bot",
  "valid_until": "2025-12-15T14:35:00Z"
}
```

### Test 5: Get Message Traces

```bash
curl -X GET http://localhost:8882/api/v1/traces \
  -H "x-api-key: omni-dev-key-test-2025"
```

**Expected Response (200 OK):**
```json
{
  "total": 1,
  "traces": [
    {
      "trace_id": "abc123def456ghi789",
      "instance_id": "whatsapp-leo-bot",
      "user_id": "whatsapp:+15551234567",
      "message_content": "What can you do?",
      "response_content": "I am Leo, your AI assistant...",
      "status": "completed",
      "duration_ms": 7850,
      "created_at": "2025-12-15T14:32:01Z"
    }
  ]
}
```

---

## WhatsApp End-to-End Testing

### Prerequisites
- Instance `whatsapp-leo-bot` created in Omni
- QR code scanned with WhatsApp mobile
- Leo adapter running and healthy
- Omni API running

### Test Steps

1. **Send Message from WhatsApp**
   - Open your test WhatsApp account
   - Send: "What can you do?"
   - Wait for response (5-8 seconds)

2. **Monitor Logs**
   - **Leo Adapter logs** (Terminal 1):
     ```
     INFO:leo-adapter:Received request from user: whatsapp:+15551234567
     INFO:leo-adapter:Calling Leo API...
     DEBUG:leo-adapter:Extracted text: "I am Leo..."
     ```
   - **Omni logs** (Terminal 2):
     ```
     INFO:Webhook received from Evolution API
     INFO:Calling agent API: http://localhost:8887
     INFO:Agent response received, sending to Evolution API
     ```

3. **Verify Response**
   - Response appears in WhatsApp within 8 seconds
   - Response starts with "I am Leo, your AI assistant"

4. **Check Traces**
   ```bash
   curl -X GET http://localhost:8882/api/v1/traces \
     -H "x-api-key: omni-dev-key-test-2025"
   ```
   - Status should be "completed"
   - Duration should be ~5-8 seconds
   - All steps should show success

---

## Automated Testing Scripts

### Quick Test Script

```python
# quick_test_leo.py
import requests
import json
import time

BASE_URL_OMNI = "http://localhost:8882"
BASE_URL_ADAPTER = "http://localhost:8887"
OMNI_API_KEY = "omni-dev-key-test-2025"
ADAPTER_API_KEY = "leo-adapter-key-2025"

# Test 1: Adapter health
print("Test 1: Adapter Health")
resp = requests.get(f"{BASE_URL_ADAPTER}/health")
print(f"  Status: {resp.status_code}")
print(f"  Response: {resp.json()}\n")

# Test 2: Direct adapter call
print("Test 2: Direct Adapter Call")
payload = {
    "user_id": "test-user-123",
    "session_id": "test-session",
    "message": "What can you do?",
    "context": {"channel": "test"},
    "session_origin": "test"
}
resp = requests.post(
    f"{BASE_URL_ADAPTER}/api/agent/chat",
    json=payload,
    headers={"X-API-Key": ADAPTER_API_KEY}
)
print(f"  Status: {resp.status_code}")
print(f"  Response: {resp.json()}\n")

# Test 3: Get traces
print("Test 3: Get Message Traces")
resp = requests.get(
    f"{BASE_URL_OMNI}/api/v1/traces",
    headers={"x-api-key": OMNI_API_KEY}
)
print(f"  Status: {resp.status_code}")
traces = resp.json().get("traces", [])
print(f"  Total traces: {len(traces)}")
if traces:
    print(f"  Latest trace: {traces[0]['trace_id']}")
```

**Run it:**
```bash
python quick_test_leo.py
```

---

## Debugging & Traceability

### Adapter Debug Output

**File:** `leo_raw_response_debug.txt`

Contains complete streaming response from Leo API:
```
event: RUN_STARTED
data: {"run_id": "run-789xyz", "status": "started"}
...
[Full response logged]
```

**To view:**
```bash
cat leo_raw_response_debug.txt
```

### Logs to Monitor

1. **Adapter Console (Terminal 1)**
   - Shows Leo API calls and responses
   - Shows parsing progress
   - Shows final extracted text

2. **Omni Console (Terminal 2)**
   - Shows webhook received
   - Shows agent API call details
   - Shows Evolution API send status

3. **Trace Records**
   - Complete message lifecycle
   - All steps with timestamps
   - Performance metrics

### Traceability Checklist

```
Message Flow Verification:
┌─ Webhook received? → Check Omni logs
├─ User allowed? → Check access control logs
├─ Agent called? → Check Omni logs + Adapter logs
├─ Leo API responded? → Check Adapter logs + leo_raw_response_debug.txt
├─ Text extracted? → Check Adapter logs
├─ Response returned to Omni? → Check Omni logs
├─ Evolution API called? → Check Omni logs
└─ WhatsApp delivered? → Check WhatsApp app + Trace record
```

---

## Troubleshooting Guide

### Problem 1: Adapter Returns "degraded" Status

**Symptom:**
```json
{
  "status": "degraded",
  "leo_api_configured": false,
  "leo_api_reachable": false
}
```

**Solutions:**
1. Check `.env.leo` file exists
2. Check `LEO_BEARER_TOKEN` is set and not expired
3. Restart adapter: `python adapter-leo-agent.py`

---

### Problem 2: 401 Unauthorized from Leo API

**Symptom:**
```
ERROR: Leo API returned 401 Unauthorized
```

**Cause:** Bearer token expired

**Solution:**
1. Open browser
2. Go to Leo dev environment
3. Open DevTools → Network tab
4. Perform any action to trigger API call
5. Look for `Authorization: Bearer eyJh...` header
6. Copy the full token (without "Bearer " prefix)
7. Update `.env.leo`: `LEO_BEARER_TOKEN=<new-token>`
8. Restart adapter

---

### Problem 3: "Could not extract text from Leo response"

**Symptom:**
```
ERROR: Could not extract text from Leo response
Returning empty response
```

**Debug Steps:**
1. Check `leo_raw_response_debug.txt`
2. Look for `TEXT_MESSAGE_CONTENT` events
3. If missing, Leo API format may have changed
4. Check adapter logs for actual event types received

**Solution:**
- Review Leo API documentation for format changes
- Update parser in `adapter-leo-agent.py` if needed

---

### Problem 4: Connection Refused to Adapter

**Symptom:**
```
Failed to connect to http://localhost:8887
```

**Solutions:**
1. Check adapter is running: `python adapter-leo-agent.py`
2. Check port 8887 is not in use: `netstat -an | findstr 8887`
3. Check firewall settings

---

### Problem 5: Timeout Calling Agent API

**Symptom:**
```
Timeout calling agent API after 120s
```

**Cause:** Leo API taking too long or not responding

**Solutions:**
1. Check network connectivity to Leo API
2. Check Leo bearer token is valid
3. Increase `AGENT_TIMEOUT` in instance config
4. Check if Leo API is experiencing issues

---

### Problem 6: WhatsApp Message Doesn't Trigger Webhook

**Symptom:**
- Message sent from WhatsApp
- No logs in Omni
- No response received

**Cause:** Webhook not registered in Evolution API

**Solution:**
1. Use `setup_leo_instance.py` to auto-configure
2. Or manually check Evolution API instance settings
3. Webhook URL should be: `http://<your-ip>:8882/webhook/evolution/whatsapp-leo-bot`

---

### Problem 7: Emoji Encoding Issues in PowerShell

**Symptom:**
```
? instead of emoji in logs
```

**Solution:**
- This is PowerShell display issue only, not real problem
- Check logs in text file instead
- Or use Windows Terminal which handles UTF-8 better

---

### Quick Reference: Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Expired token | Get fresh token from browser |
| 422 Validation Error | Missing required field | Check request payload format |
| Connection refused | Service not running | Start adapter: `python adapter-leo-agent.py` |
| Timeout after 120s | Leo API slow/down | Check Leo API status, increase timeout |
| No response in WhatsApp | Webhook not registered | Run `setup_leo_instance.py` |
| "Could not extract text" | Leo response format changed | Check `leo_raw_response_debug.txt` |

---

## Summary

This guide covers all aspects of testing the Automagic Omni ↔ Leo integration:
- ✅ Complete end-to-end example with all API calls
- ✅ Request/response payloads at each stage
- ✅ Manual testing procedures (curl/Postman)
- ✅ WhatsApp end-to-end testing
- ✅ Automated test scripts
- ✅ Comprehensive debugging techniques
- ✅ Troubleshooting for common issues

**Next step:** Follow the [COMPLETE_SETUP_AND_CONFIGURATION_GUIDE.md](COMPLETE_SETUP_AND_CONFIGURATION_GUIDE.md) to set up your system, then return here to test.

---

*Last Updated: December 15, 2025*
