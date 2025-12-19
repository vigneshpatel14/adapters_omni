# COMPLETE SETUP & CONFIGURATION GUIDE: Automagic Omni ↔ Leo Streaming Agent Integration

**Last Updated:** December 15, 2025  
**Status:** Production Ready  
**Version:** 2.0

---

## Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [System Architecture Deep Dive](#system-architecture-deep-dive)
3. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
4. [Installation & Dependency Setup](#installation--dependency-setup)
5. [Configure Automagic Omni](#configure-automagic-omni)
6. [Starting Services](#starting-services)
7. [Creating & Configuring Instances](#creating--configuring-instances)
8. [Multi-Tenant Architecture](#multi-tenant-architecture)
9. [Security & Access Control](#security--access-control)
10. [Database Schema & Models](#database-schema--models)
11. [Troubleshooting Setup Issues](#troubleshooting-setup-issues)

---

## Overview & Architecture

### What is Automagic Omni?

**Automagic Omni** is a production-grade, multi-tenant omnichannel messaging hub that:
- Receives messages from WhatsApp (via Evolution API), Discord, Slack, and other platforms
- Routes messages to your custom AI agent for processing
- Returns responses back through the same channel
- Maintains complete audit trails with message tracing
- Supports multiple isolated tenants with separate configurations

### Leo Agent Integration

**Leo Agent is now integrated directly into Omni!**

Omni includes a built-in `LeoAgentClient` that:
- Automatically detects Leo API URLs in instance configuration
- Handles Leo's streaming (SSE) response format
- Parses deltas and concatenates text responses
- Manages authentication using .env credentials
- No separate adapter service needed!

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  EXTERNAL CHANNELS (WhatsApp, Discord, Slack)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Evolution API│  │Discord Bots  │  │ Slack API    │          │
│  │ (WhatsApp)   │  │              │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │ Webhook          │ IPC             │ API
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  AUTOMAGIK OMNI API (Port 8882)                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ POST /webhook/evolution/{instance}     (WhatsApp Webhook) │ │
│  │ POST /api/v1/instances                 (Instance CRUD)    │ │
│  │ GET  /api/v1/instances/{name}          (Get Instance)    │ │
│  │ PUT  /api/v1/instances/{name}          (Update Instance)  │ │
│  │ GET  /api/v1/traces                    (Message Traces)   │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Built-in Services:                                         │ │
│  │ - Message Router: Route to agent                          │ │
│  │ - LeoAgentClient: Built-in Leo integration               │ │
│  │ - Trace Service: Log message lifecycle                    │ │
│  │ - Access Control: Permission checks                       │ │
│  │ - User Service: User/session management                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────┬───────────────────────────────────────────────────────────┘
       │ Direct Leo API call (auto-detected from instance config)
       │ Uses credentials from .env file
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  LEO STREAMING API (Remote)                                     │
│  POST /leo-portal-agentic-runtime-node-api/v1/stream           │
│  Headers: Authorization: Bearer <token>                        │
│           X-Subscription-Key: <key>                            │
│                                                                 │
│  - Processes message via workflow                              │
│  - Returns Server-Sent Events (SSE) stream                     │
│  - Omni parses and assembles final response                    │
└─────────────────────────────────────────────────────────────────┘
```

**Message Flow:**

WhatsApp → Evolution API → Omni Webhook → LeoAgentClient (built-in) → Leo API

Leo API → LeoAgentClient (built-in) → Omni Response Handler → Evolution API → WhatsApp
│  - Streams response as SSE with TEXT_MESSAGE_CONTENT deltas   │
│  - Supports multi-turn conversations                           │
└─────────────────────────────────────────────────────────────────┘
```

### Key Flows

**Message Incoming:**
```
WhatsApp → Evolution API → Omni Webhook → LeoAgentClient (built-in) → Leo API
```

**Message Outgoing:**
```
Leo API → LeoAgentClient (built-in) → Omni Response Handler → Evolution API → WhatsApp
```

---

## System Architecture Deep Dive

### 1. Multi-Tenant Isolation

Each instance (tenant) has:
- **Unique instance name** (e.g., `whatsapp-leo-bot`)
- **Separate Evolution API credentials** (URL, API key, instance name)
- **Separate agent endpoint** (URL + API key)
- **Dedicated webhook URL** for receiving messages
- **Independent database records** for messages and traces
- **Isolated access control** rules (allow/block lists)

**Isolation Guarantee:**
```
Instance A (Company X)
├─ Evolution API URL: https://evolution-api-a.example.com
├─ Evolution API Key: KEY_A
├─ Agent URL: http://agent-a.example.com
├─ Webhook URL: /webhook/evolution/company-x
└─ Database: Separate trace records

Instance B (Company Y)
├─ Evolution API URL: https://evolution-api-b.example.com
├─ Evolution API Key: KEY_B
├─ Agent URL: http://agent-b.example.com
├─ Webhook URL: /webhook/evolution/company-y
└─ Database: Separate trace records
```

### 2. Message Processing Pipeline

```
1. WEBHOOK RECEIVED
   - Evolution API POSTs message to Omni webhook
   - Omni parses message data
   - Creates MessageTrace record (status: pending)

2. INSTANCE VALIDATION
   - Look up instance by name
   - Validate instance is active
   - Validate instance configuration

3. ACCESS CONTROL CHECK
   - Check allow/block lists
   - Check user is permitted
   - Create trace entry

4. AGENT API CALL
   - Translate message to agent format
   - Call agent endpoint with timeout
   - Create trace entry with agent response

5. RESPONSE PROCESSING
   - Parse agent response
   - Validate response format
   - Create trace entry

6. SEND TO CHANNEL
   - Call Evolution API with response
   - Specify recipient from original message
   - Create trace entry with send status

7. TRACE COMPLETION
   - Update trace status: completed
   - Record total duration
   - Log all steps
```

### 3. Agent API Contract

Every agent endpoint must support:

**Request Format:**
```json
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

**Response Format:**
```json
{
  "text": "Response text from agent"
}
```

**Endpoint:** `POST /api/agent/chat` or custom (configured per instance)

---

## Prerequisites & Environment Setup

### System Requirements

- **OS:** Windows, macOS, or Linux
- **Python:** 3.8 or later
- **pip/uv:** Package manager
- **Database:** SQLite (default) or PostgreSQL
- **Network:** Internet access for Evolution API and Leo API

### Software to Install

```powershell
# Python 3.8+
python --version

# pip (usually comes with Python)
pip --version

# Optional: uv package manager (faster)
pip install uv
uv --version
```

### Environment Variables Needed

**For Omni (`.env` file):**
```env
# API Configuration
AUTOMAGIK_OMNI_API_KEY=your-random-secure-key
AUTOMAGIK_OMNI_API_HOST=0.0.0.0
AUTOMAGIK_OMNI_API_PORT=8882

# Database
AUTOMAGIK_OMNI_SQLITE_DATABASE_PATH=./data/automagik-omni.db

# Evolution API (Default - used for new instances if not specified)
EVOLUTION_API_URL=https://evolution-api-production-7611.up.railway.app
EVOLUTION_API_KEY=FA758317-709D-4BB6-BA4F-987B2335036A

# Server Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
AUTOMAGIK_OMNI_TIMEZONE=UTC
AUTOMAGIK_OMNI_ENABLE_TRACING=true
```

**For Leo Adapter (`.env.leo` file):**
```env
# Leo API Credentials
LEO_BEARER_TOKEN=eyJhbGciOiJIUzI1NiIs...  # Get from browser DevTools
LEO_WORKFLOW_ID=e9f65742-8f61-4a7f-b0d2-71b77c5391e7
LEO_API_BASE_URL=https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1
LEO_SUBSCRIPTION_KEY=018ca54b...

# Adapter Configuration
ADAPTER_API_KEY=leo-adapter-key-2025
ADAPTER_PORT=8887
ADAPTER_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
```

---

## Installation & Dependency Setup

### Step 1: Clone Repository

```powershell
# Navigate to workspace
cd c:\Automagic_Omni

# Verify git repo is cloned
git status

# Update submodules if needed
git submodule update --init --recursive
```

### Step 2: Create Virtual Environment

```powershell
# Option A: Using uv (recommended)
uv venv

# Option B: Using venv
python -m venv venv

# Activate
# On Windows:
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```powershell
# Option A: Using uv (faster)
uv sync

# Option B: Using pip
pip install -r requirements.txt
# OR if pyproject.toml:
pip install -e .

# Install specific packages needed:
pip install fastapi uvicorn pydantic requests python-dotenv sqlalchemy
```

### Step 4: Initialize Database

```powershell
# Run migrations
python -m alembic upgrade head

# Or manually:
python -c "from src.db.models import Base; from src.db.database import engine; Base.metadata.create_all(bind=engine)"

# Verify database created
ls -la data/automagik-omni.db
```

---

## Configure Automagic Omni

### Step 1: Create `.env` File

```powershell
# Copy template
cp .env.example .env

# Edit with your values
notepad .env
```

### Step 2: Configure Required Fields

```env
# API Security
AUTOMAGIK_OMNI_API_KEY=your-super-secure-random-key-here-min-32-chars

# Port Configuration
AUTOMAGIK_OMNI_API_HOST=0.0.0.0
AUTOMAGIK_OMNI_API_PORT=8882

# Database
AUTOMAGIK_OMNI_SQLITE_DATABASE_PATH=./data/automagik-omni.db

# Evolution API (Default for new instances)
EVOLUTION_API_URL=https://evolution-api-production-7611.up.railway.app
EVOLUTION_API_KEY=FA758317-709D-4BB6-BA4F-987B2335036A

# Logging
ENVIRONMENT=development
LOG_LEVEL=INFO
AUTOMAGIK_OMNI_TIMEZONE=UTC
AUTOMAGIK_OMNI_ENABLE_TRACING=true

# CORS Origins (for web UI if needed)
AUTOMAGIK_OMNI_CORS_ORIGINS=http://localhost:3000,http://localhost:8888
```

### Step 3: Verify Configuration

```powershell
# Test API key generation
$key = -join ((48..57) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Generated API Key: $key"

# Update in .env
```

---

## Starting All Services

### Service 1: Automagic Omni API (Port 8882)

```powershell
# Terminal 1
cd c:\Automagic_Omni

# Activate venv if not already
.\venv\Scripts\Activate.ps1

# Start Omni API
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8882 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8882
# INFO:     Application startup complete
```

**Health Check:**
```powershell
curl http://localhost:8882/health
# Response: {"status": "ok"}
```

✅ **Omni is now running with Leo integration built-in!**

Leo credentials are read from .env file automatically. No separate adapter service needed.

### (Optional) Echo Agent for Testing (Port 8886)

```powershell
# Terminal 3
cd c:\Automagic_Omni

# Start Echo Agent
python agent-echo.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8886
```

### Verify All Services Running

```powershell
# Check all three ports are listening
netstat -ano | findstr :8882
netstat -ano | findstr :8887
netstat -ano | findstr :8886

# Or test with curl
curl http://localhost:8882/health  # Omni
curl http://localhost:8887/health  # Leo Adapter
curl http://localhost:8886/health  # Echo Agent
```

---

## Creating & Configuring Instances

### Option 1: Automated Setup Script

```powershell
python setup_leo_instance.py

# Expected output:
# ✅ Leo adapter health: healthy
# ✅ Creating WhatsApp instance: whatsapp-leo-bot
# ✅ Instance created successfully
# ✅ QR code available
```

### Option 2: Complete Postman Walkthrough (Step-by-Step)

This section shows the complete flow from creating an instance to sending a message via WhatsApp.

#### **Step 1: Create WhatsApp Instance with Leo Agent**

**Open Postman and create a new request:**

**Request Details:**
```
Method: POST
URL: http://localhost:8882/api/v1/instances
```

**Headers Tab:**
```
Key                 Value
Content-Type        application/json
x-api-key           omni-dev-key-test-2025
```

**Body Tab (Raw JSON):**
```json
{
  "name": "whatsapp-leo-bot",
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

**About the configuration:**
- `agent_api_url`: Leo's streaming endpoint (Omni auto-detects "api-leodev.gep.com" and uses built-in LeoAgentClient)
- `agent_api_key`: Can be any value (real auth uses .env credentials)
- `default_agent`: "leo" (triggers Leo integration)
- Leo credentials loaded automatically from .env file

**Click "Send":**

**What's Happening Behind the Scenes:**
1. Omni API receives POST request with instance configuration
2. Validates all required fields are present
3. Looks up Evolution API endpoint to verify connectivity
4. Creates database record in `InstanceConfig` table
5. Auto-registers webhook URL in Evolution API if `auto_qr: true`
6. Generates QR code for WhatsApp pairing
7. Returns instance details with ID

**Expected Response (201 Created):**
```json
{
  "id": 1,
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
  "created_at": "2025-12-15T14:20:00Z",
  "updated_at": "2025-12-15T14:20:00Z"
}
```

**What this means:**
- ✅ Instance created successfully in Omni database
- ✅ Webhook registered in Evolution API
- ✅ Ready for WhatsApp pairing (next step: QR code)

---

#### **Step 2: Get QR Code for WhatsApp Pairing**

**In Postman, create new request:**

**Request Details:**
```
Method: GET
URL: http://localhost:8882/api/v1/instances/whatsapp-leo-bot/qr
```

**Headers Tab:**
```
Key         Value
x-api-key   omni-dev-key-test-2025
```

**Click "Send":**

**What's Happening Behind the Scenes:**
1. Omni API receives GET request for QR code
2. Looks up instance by name in database
3. Calls Evolution API to get current QR code for that instance
4. Evolution API generates fresh QR code (valid for ~5 minutes)
5. Returns QR code as base64-encoded PNG image data

**Expected Response (200 OK):**
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADCAYAAADJS2sFAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAuIwAALiMBeKU/dgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAeISURBVHic7d1...",
  "instance_name": "whatsapp-leo-bot",
  "valid_until": "2025-12-15T14:25:00Z",
  "instance_id": 1
}
```

**What this means:**
- ✅ QR code generated successfully
- ✅ Valid for 5 minutes (see `valid_until`)
- ✅ Ready to scan with WhatsApp mobile app

**Next Action:**
1. Copy the QR code data
2. Use an online QR decoder or Postman's QR visualization (if available)
3. Scan with WhatsApp mobile app on your test phone
4. This connects your WhatsApp account to the bot instance

---

#### **Step 3: Wait for WhatsApp Connection**

**After scanning QR code:**
- WhatsApp will show "Syncing..." on your phone
- Bot instance will connect to Evolution API
- Connection is ready when QR code expires or app shows connected

**Time:** Usually 10-30 seconds

---

#### **Step 4: Manually Trigger Webhook (Simulate Message)**

This simulates what happens when you send a real WhatsApp message.

**In Postman, create new request:**

**Request Details:**
```
Method: POST
URL: http://localhost:8882/webhook/evolution/whatsapp-leo-bot
```

**Headers Tab:**
```
Key             Value
Content-Type    application/json
```

**Body Tab (Raw JSON) - This simulates Evolution API webhook:**
```json
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

**Click "Send":**

**What's Happening Behind the Scenes (5 API Calls in Sequence):**

1. **Webhook Received in Omni**
   - Endpoint: `/webhook/evolution/whatsapp-leo-bot`
   - Omni parses message data from Evolution API format
   - Extracts: sender phone (+15551234567), message text ("What can you do?")
   - Creates `MessageTrace` record in database with status: "pending"
   - Logs: "Webhook received from Evolution API for instance: whatsapp-leo-bot"

2. **Instance Validation**
   - Looks up instance config in database
   - Validates instance is active and properly configured
   - Checks all required fields (agent_url, agent_key, timeout)
   - Creates trace step: "instance_validated" ✓

3. **Access Control Check**
   - Checks if user phone number is in allow/block lists
   - User +15551234567 is allowed (not in blocklist)
   - Creates trace step: "access_control_checked" ✓

4. **Call Leo Adapter (Agent API)**
   - **Omni → Leo Adapter Call:**
     ```
     POST http://localhost:8887/api/agent/chat
     Headers: X-API-Key: leo-adapter-key-2025
     Content-type: application.json
     Body:
     {"user_id":"test-123","session_id":"test-session","session_name":"test","message":"hello"}
     ```
   
   - **Leo Adapter processes:**
     - Validates Omni API key ✓
     - Translates format to Leo API format
     - Calls Leo streaming API with bearer token
     - Receives SSE stream with TEXT_MESSAGE_CONTENT deltas
     - Concatenates: "I am Leo, your AI assistant..."
     - Returns to Omni
   
   - **Leo Adapter → Omni Response:**
     ```json
     {
       "text": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!"
     }
     ```
   - Creates trace step: "agent_called" with duration ✓

5. **Send Response Back to WhatsApp (Evolution API)**
   - **Omni → Evolution API Call:**
     ```
     POST https://evolution-api-production-7611.up.railway.app/message/sendText/whatsapp-leo-bot
     Headers: X-API-Key: FA758317-709D-4BB6-BA4F-987B2335036A
     Body:
     {
       "number": "+15551234567",
       "text": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!",
       "delay": 100
     }
     ```
   
   - **Evolution API processes:**
     - Queues message for WhatsApp delivery
     - Returns confirmation with message ID
   
   - **Evolution API → Omni Response:**
     ```json
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
   - Creates trace step: "evolution_api_called" ✓

**Expected Response from Postman (200 OK):**
```json
{
  "status": "received",
  "trace_id": "abc123def456ghi789",
  "message": "Message processed successfully"
}
```

**What this means:**
- ✅ Webhook received and validated
- ✅ Instance found and active
- ✅ User allowed by access control
- ✅ Agent API called successfully
- ✅ Response sent to Evolution API
- ✅ Evolution API confirmed message queued
- ✅ Message will appear in WhatsApp within seconds

---

#### **Step 5: View Message Trace (Complete Lifecycle)**

**In Postman, create new request:**

**Request Details:**
```
Method: GET
URL: http://localhost:8882/api/v1/traces
```

**Headers Tab:**
```
Key         Value
x-api-key   omni-dev-key-test-2025
```

**Click "Send":**

**What's Happening Behind the Scenes:**
1. Omni looks up all message traces in database
2. Returns complete message lifecycle for your request
3. Shows all processing steps with timestamps and status

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
      "response_content": "I am Leo, your AI assistant. I can help you with questions, analysis, coding, and much more!",
      "status": "completed",
      "duration_ms": 7850,
      "created_at": "2025-12-15T14:32:01Z",
      "completed_at": "2025-12-15T14:32:08Z",
      "evolution_api_success": true,
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
          "response_preview": "I am Leo, your AI assistant...",
          "timestamp": "2025-12-15T14:32:09Z"
        },
        {
          "step": "evolution_api_called",
          "status": "success",
          "message_sent": true,
          "timestamp": "2025-12-15T14:32:10Z"
        }
      ]
    }
  ]
}
```

**What this means:**
- ✅ Complete message lifecycle captured
- ✅ All 5 processing steps completed successfully
- ✅ Total processing time: 7.85 seconds
- ✅ Message trace shows exactly what happened at each stage
- ✅ Can be used for debugging if issues occur

---

#### **Step 6: Send Real WhatsApp Message (Optional)**

Once QR code is scanned and verified connected:

1. Open WhatsApp on your test phone
2. Send message to the bot's WhatsApp number
3. Should receive Leo's response within 8 seconds
4. Check traces again to see real message recorded

---

### Option 3: Manual Creation via curl

```powershell
$payload = @{
    "name" = "whatsapp-leo-bot"
    "evolution_url" = "https://evolution-api-production-7611.up.railway.app"
    "evolution_key" = "FA758317-709D-4BB6-BA4F-987B2335036A"
    "whatsapp_instance" = "whatsapp-leo-bot"
    "agent_api_url" = "http://localhost:8887"
    "agent_api_key" = "leo-adapter-key-2025"
    "default_agent" = "leo-adapter"
    "agent_timeout" = 120
    "webhook_base64" = $false
    "is_active" = $true
    "is_default" = $false
    "auto_qr" = $true
} | ConvertTo-Json

curl -X POST http://localhost:8882/api/v1/instances `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -Body $payload

# Response should show instance created with ID
```

### Creating Discord Instance

Discord instances are created similarly but with different configuration fields for bot authentication.

**Request:**
```
POST http://localhost:8882/api/v1/instances
Headers:
  Content-Type: application/json
  x-api-key: omni-dev-key-test-2025

Body:
{
  "name": "discord-leo-bot",
  "discord_bot_token": "MTk4NjIyNDgzNjI0MDMyMjU4.CXY2_A.ZV...",
  "discord_client_id": "198622483624032258",
  "discord_guild_id": "123456789012345678",
  "discord_default_channel_id": "234567890123456789",
  "discord_voice_enabled": false,
  "discord_slash_commands_enabled": true,
  "discord_permissions": 8,
  "agent_api_url": "http://localhost:8887",
  "agent_api_key": "leo-adapter-key-2025",
  "default_agent": "leo-adapter",
  "agent_timeout": 120,
  "is_active": true,
  "is_default": false
}
```

**Discord Configuration Fields Explained:**

| Field | Description | Example |
|-------|-------------|---------|
| `discord_bot_token` | Bot's authentication token (get from Discord Developer Portal) | `MTk4NjIyNDgzNjI0MDMyMjU4.CXY2_A.ZV...` |
| `discord_client_id` | Application/Bot Client ID from Developer Portal | `198622483624032258` |
| `discord_guild_id` | (Optional) Specific server/guild ID for bot to join | `123456789012345678` |
| `discord_default_channel_id` | (Optional) Default text channel for messages | `234567890123456789` |
| `discord_voice_enabled` | Enable voice channel support | `false` |
| `discord_slash_commands_enabled` | Enable Discord slash commands | `true` |
| `discord_permissions` | Permission integer (8 = Administrator) | `8` |
| `discord_webhook_url` | (Optional) Webhook for outbound notifications | `https://discordapp.com/api/webhooks/...` |

**How to Get Discord Credentials:**

1. **Create Discord Application:**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Give it a name (e.g., "Leo Bot")
   - Copy `Client ID` → Use as `discord_client_id`

2. **Create Bot Token:**
   - In application page, go to "Bot" section
   - Click "Add Bot"
   - Under TOKEN section, click "Copy" → Use as `discord_bot_token`
   - **⚠️ KEEP THIS SECRET!** Don't share or commit to git

3. **Get Guild/Server ID:**
   - Open Discord, go to your server
   - Right-click server name → Copy Server ID
   - Use as `discord_guild_id`

4. **Get Channel ID:**
   - In Discord, right-click a text channel → Copy Channel ID
   - Use as `discord_default_channel_id`

5. **Set Permissions:**
   - In Developer Portal, go to "OAuth2" → "URL Generator"
   - Select scopes: `bot`
   - Select permissions needed (or `Administrator` = 8)
   - Copy generated URL → Use to invite bot to server

---

### Option 3: Manual Creation via curl

### Get QR Code for WhatsApp Scanning

```powershell
curl http://localhost:8882/api/v1/instances/whatsapp-leo-bot/qr `
  -H "x-api-key: omni-dev-key-test-2025"

# Response: {"qr_code": "data:image/png;base64,...", ...}

# Copy the QR code and scan with WhatsApp mobile
# Or save as file:
curl http://localhost:8882/api/v1/instances/whatsapp-leo-bot/qr `
  -H "x-api-key: omni-dev-key-test-2025" > qr_response.json
```

### List All Instances

```powershell
curl http://localhost:8882/api/v1/instances `
  -H "x-api-key: omni-dev-key-test-2025"

# Response: [{"id": 1, "name": "whatsapp-leo-bot", ...}]
```

### Update Instance Configuration

```powershell
curl -X PUT http://localhost:8882/api/v1/instances/whatsapp-leo-bot `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -d '{
    "agent_timeout": 150,
    "agent_api_url": "http://localhost:8887"
  }'
```

---

## Leo Adapter Configuration

### Step 1: Create `.env.leo` File

```powershell
# Copy template
cp .env.leo-adapter .env.leo

# Edit with your credentials
notepad .env.leo
```

### Step 2: Add Leo API Credentials

```env
# Get LEO_BEARER_TOKEN from browser:
# 1. Open Leo dev environment in browser
# 2. Open DevTools (F12)
# 3. Go to Network tab
# 4. Perform any action to trigger API call
# 5. Look for request with Authorization header
# 6. Copy full token value (without "Bearer " prefix)

LEO_BEARER_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Other Leo credentials (from your Leo account)
LEO_WORKFLOW_ID=e9f65742-8f61-4a7f-b0d2-71b77c5391e7
LEO_API_BASE_URL=https://api-leodev.gep.com/leo-portal-agentic-runtime-node-api/v1
LEO_SUBSCRIPTION_KEY=018ca54b...

# Adapter settings
ADAPTER_API_KEY=leo-adapter-key-2025
ADAPTER_HOST=0.0.0.0
ADAPTER_PORT=8887

# Logging
LOG_LEVEL=INFO
```

### Step 3: Update Leo Bearer Token (When Expired)

Leo tokens expire periodically. To refresh:

```powershell
# 1. Open browser with Leo dev environment
# 2. Press F12 to open DevTools
# 3. Go to Network tab
# 4. Perform a Leo action (click a button, etc.)
# 5. Find the request with Authorization header
# 6. Copy new token
# 7. Update .env.leo:

notepad .env.leo
# Update: LEO_BEARER_TOKEN=<new-token>

# 8. Restart adapter:
# Stop current: Ctrl+C
# Restart: python adapter-leo-agent.py
```

### Adapter Configuration Options

```env
# Core
ADAPTER_API_KEY=leo-adapter-key-2025          # For Omni to authenticate
ADAPTER_PORT=8887                             # Port to listen on
ADAPTER_HOST=0.0.0.0                          # Listen on all interfaces

# Leo API
LEO_BEARER_TOKEN=<your-token>                 # Authentication
LEO_SUBSCRIPTION_KEY=<your-key>               # Subscription validation
LEO_API_BASE_URL=<leo-api-url>                # API endpoint
LEO_WORKFLOW_ID=<workflow-id>                 # Workflow to use

# Features
ENABLE_DEBUG_LOGGING=true                     # Log raw Leo responses
DEBUG_OUTPUT_FILE=leo_raw_response_debug.txt  # Where to save debug logs

# Timeouts
REQUEST_TIMEOUT=120                           # Seconds to wait for Leo response
```

---

## Multi-Tenant Architecture

### Creating Multiple Instances

Each instance is completely isolated:

```powershell
# Instance 1: Company A
curl -X POST http://localhost:8882/api/v1/instances `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -d '{
    "name": "company-a-bot",
    "evolution_url": "https://evolution-api-a.example.com",
    "evolution_key": "KEY-A",
    "agent_api_url": "http://agent-a.example.com:8000",
    "agent_api_key": "KEY-AGENT-A"
  }'

# Instance 2: Company B
curl -X POST http://localhost:8882/api/v1/instances `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -d '{
    "name": "company-b-bot",
    "evolution_url": "https://evolution-api-b.example.com",
    "evolution_key": "KEY-B",
    "agent_api_url": "http://agent-b.example.com:8000",
    "agent_api_key": "KEY-AGENT-B"
  }'
```

### Data Isolation

Each instance:
- Has separate webhook URL: `/webhook/evolution/{instance_name}`
- Has separate database records
- Has separate message traces
- Cannot access other instance's data
- Has independent access control rules

### Scaling Multi-Tenant

```
Multiple Omni Instances (Load Balanced)
├─ Omni-1 (Port 8882)
├─ Omni-2 (Port 8883)
└─ Omni-3 (Port 8884)

Multiple Leo Adapters
├─ Leo Adapter-1 (Port 8887)
├─ Leo Adapter-2 (Port 8888)
└─ Leo Adapter-3 (Port 8889)

Shared PostgreSQL Database
└─ All instances share one database with tenant isolation via instance_id
```

---

## Security & Access Control

### Channel-Specific Credentials

Each channel type has different authentication requirements:

**WhatsApp (Evolution API):**
- Evolution API URL
- Evolution API Key
- Evolution Instance Name

**Discord:**
- Discord Bot Token (keep secret!)
- Discord Client ID
- Discord Guild ID (optional)
- Discord Channel ID (optional)
- Discord Permissions Integer

**Slack (Future):**
- Slack Bot Token
- Slack Workspace URL
- Slack App ID

### API Key Management

```powershell
# Generate random secure keys
# Option 1: PowerShell
$key = -join ((48..57) + (97..122) + (65..90) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Option 2: Python
python -c "import secrets; print(secrets.token_hex(16))"

# Store in .env files
AUTOMAGIK_OMNI_API_KEY=<secure-key-for-omni>
ADAPTER_API_KEY=<secure-key-for-adapter>
```

### Access Control (Allow/Block Lists)

```powershell
# Block specific user
curl -X POST http://localhost:8882/api/v1/instances/whatsapp-leo-bot/access-control `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -d '{
    "action": "block",
    "phone_number": "+1234567890"
  }'

# Allow specific user
curl -X POST http://localhost:8882/api/v1/instances/whatsapp-leo-bot/access-control `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -d '{
    "action": "allow",
    "phone_number": "+9876543210"
  }'

# List access control rules
curl http://localhost:8882/api/v1/instances/whatsapp-leo-bot/access-control `
  -H "x-api-key: omni-dev-key-test-2025"
```

### Per-Instance Secrets

Each instance has:
- Separate Evolution API key
- Separate agent API key
- Separate Leo adapter key (if using Leo)
- No shared secrets between instances

### Transport Security

**Production Settings:**
```env
# Use HTTPS for API endpoints
AUTOMAGIK_OMNI_API_SCHEME=https

# Restrict CORS origins
AUTOMAGIK_OMNI_CORS_ORIGINS=https://yourdomain.com

# Rate limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=60
```

---

## Database Schema & Models

### Core Tables

**InstanceConfig** - Instance configurations
```
id (PK)
name (UNIQUE) - Instance identifier
evolution_url
evolution_key
evolution_instance
agent_api_url
agent_api_key
default_agent
agent_timeout
webhook_base64
is_active
is_default
created_at
updated_at
```

**MessageTrace** - Message processing history
```
id (PK)
trace_id (UNIQUE)
instance_id (FK)
user_id
message_content
response_content
status (pending/completed/failed)
duration_ms
steps (JSON) - Each step in processing
created_at
completed_at
evolution_api_success
```

**AccessControl** - Allow/block rules
```
id (PK)
instance_id (FK)
action (allow/block)
phone_number
created_at
```

### Creating Custom Tables

```powershell
# Edit alembic/versions/your_migration.py
# Then run:
python -m alembic upgrade head

# Or create directly in code:
# src/db/models.py - Add model
# python -c "from src.db.models import Base; from src.db.database import engine; Base.metadata.create_all(bind=engine)"
```

---

## Troubleshooting Setup Issues

### Issue 1: "Port already in use"

**Symptom:**
```
ERROR: Port 8882 is already in use
```

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8882

# Kill process
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn src.api.app:app --port 8883
```

### Issue 2: "Could not connect to database"

**Symptom:**
```
ERROR: unable to open database file
```

**Solution:**
```powershell
# Create data directory
mkdir -p data

# Check path in .env
cat .env | findstr DATABASE_PATH

# Ensure full path or relative path is correct
# Set in .env: ./data/automagik-omni.db
```

### Issue 3: "Leo API returns 401 Unauthorized"

**Symptom:**
```
ERROR: Leo API returned 401 Unauthorized
```

**Solution:**
```powershell
# Get fresh Leo bearer token:
# 1. Open browser with Leo dev environment
# 2. Press F12, go to Network tab
# 3. Perform an action
# 4. Find Authorization header
# 5. Copy token
# 6. Update .env.leo
notepad .env.leo

# Restart adapter
# Stop: Ctrl+C
# Restart: python adapter-leo-agent.py
```

### Issue 4: "Instance not found"

**Symptom:**
```
ERROR: Instance whatsapp-leo-bot not found
```

**Solution:**
```powershell
# List instances
curl http://localhost:8882/api/v1/instances `
  -H "x-api-key: omni-dev-key-test-2025"

# Create if missing
python setup_leo_instance.py
```

### Issue 5: "Failed to parse webhook"

**Symptom:**
```
ERROR: Failed to parse webhook JSON
```

**Cause:** Evolution API format changed or payload incorrect

**Solution:**
```powershell
# Check Evolution API webhook settings
# Ensure payload format is "raw JSON"
# Check "Webhook Base64" setting matches instance config

# Update instance if needed:
curl -X PUT http://localhost:8882/api/v1/instances/whatsapp-leo-bot `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -d '{"webhook_base64": false}'
```

### Issue 6: "Agent API timeout"

**Symptom:**
```
ERROR: Timeout calling agent API after 120s
```

**Solution:**
```powershell
# Increase timeout in instance config
curl -X PUT http://localhost:8882/api/v1/instances/whatsapp-leo-bot `
  -H "Content-Type: application/json" `
  -H "x-api-key: omni-dev-key-test-2025" `
  -d '{"agent_timeout": 180}'

# Check if Leo API is responding slowly
curl http://localhost:8887/health

# Or agent service is down
curl http://localhost:8887/api/agent/chat
```

---

## Quick Reference: Common Commands

### Health Checks
```powershell
curl http://localhost:8882/health          # Omni
curl http://localhost:8887/health          # Leo Adapter
curl http://localhost:8886/health          # Echo Agent
```

### Create Instance
```powershell
python setup_leo_instance.py
# Or curl the API (see section above)
```

### Get QR Code
```powershell
curl http://localhost:8882/api/v1/instances/whatsapp-leo-bot/qr `
  -H "x-api-key: omni-dev-key-test-2025"
```

### View Message Traces
```powershell
curl http://localhost:8882/api/v1/traces `
  -H "x-api-key: omni-dev-key-test-2025"
```

### View Leo Debug Output
```powershell
cat leo_raw_response_debug.txt
```

### Restart Services
```powershell
# Terminal 1 (Omni): Ctrl+C, then python -m src
# Terminal 2 (Adapter): Ctrl+C, then python adapter-leo-agent.py
```

---

## Next Steps

1. **Setup:** Follow this guide to configure all services
2. **Testing:** Move to [COMPLETE_TESTING_GUIDE.md](COMPLETE_TESTING_GUIDE.md) for comprehensive testing
3. **Production:** Review security section and deploy accordingly
4. **Monitoring:** Set up logging and alerting for production

---

*Last Updated: December 15, 2025*
*For issues or questions, check the Testing Guide or troubleshooting sections above.*
