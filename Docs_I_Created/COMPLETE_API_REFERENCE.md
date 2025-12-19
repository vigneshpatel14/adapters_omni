# Automagic Omni - Complete API Reference & Testing Guide

**Date:** December 12, 2025  
**Version:** 2.0 (Complete Edition)  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Environment Setup](#environment-setup)
4. [Core API Endpoints](#core-api-endpoints)
   - [Instance Management](#instance-management)
   - [WhatsApp Specific](#whatsapp-specific)
   - [Discord Specific](#discord-specific)
   - [Slack Specific](#slack-specific)
   - [Trace & Monitoring](#trace--monitoring)
5. [Channel-Specific Testing](#channel-specific-testing)
6. [Agent API](#agent-api)
7. [Advanced Features](#advanced-features)
8. [Postman Collection](#postman-collection)

---

## Overview

**Automagic Omni** is a **multi-channel** AI agent messaging hub that:
- Receives messages from **WhatsApp, Discord, Slack** (and more coming)
- Routes to AI agents for intelligent processing
- Returns responses formatted for each channel
- Maintains complete audit trails with advanced tracing

### Supported Channels

| Channel | Status | Features |
|---------|--------|----------|
| **WhatsApp** | ✅ Production | Text, media, audio, stickers, reactions, QR login |
| **Discord** | ✅ Production | Multi-server, text, embeds, reactions, voice infrastructure, IPC |
| **Slack** | 🔄 Q4 2025 | Workspace, threads, reactions, files |
| **Others** | 📅 2026+ | Instagram, Telegram, Teams, LinkedIn, WeChat, SMS |

### Key Components

| Component | Port | Purpose |
|-----------|------|---------|
| **Omni API** | 8882 | Multi-channel webhook receiver & instance management |
| **Echo Agent** | 8886 | AI agent for message processing |
| **Evolution API** | 18082 | WhatsApp gateway (local or cloud) |
| **Discord Bot** | IPC | Discord multi-bot orchestration |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTOMAGIC OMNI HUB                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌───────────────┐      ┌──────────┐ │
│  │   WhatsApp   │─────▶│   Instance    │─────▶│   AI     │ │
│  │   Webhook    │      │   Router      │      │  Agent   │ │
│  │ (Evolution)  │      │               │      │          │ │
│  └──────────────┘      └───────────────┘      └──────────┘ │
│         │                      │                             │
│  ┌──────▼──────┐               │                             │
│  │   Discord   │─────────────┤                             │
│  │   Bot + IPC │             │                             │
│  └─────────────┘             │                             │
│         │           ┌─────────▼──────┐                      │
│  ┌──────▼──────┐   │   Message      │      ┌──────────┐   │
│  │   Slack     │──▶│   Router       │─────▶│  Trace   │   │
│  │  (Q4 2025)  │   │  & Handler     │      │  Store   │   │
│  └─────────────┘   └────────────────┘      └──────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Setup

### Prerequisites

- Python 3.12+
- PostgreSQL (recommended) or SQLite (dev)
- Node.js 20+ (for Evolution API)
- Postman (for API testing)

### Base URLs

```
Omni API:      http://localhost:8882
Agent API:     http://localhost:8886
Evolution API: http://localhost:18082 (local) or cloud URL
```

### Authentication

```
Omni API Key:        omni-dev-key-test-2025
Evolution API Key:   FA758317-709D-4BB6-BA4F-987B2335036A
Discord Bot Token:   (get from Discord Developer Portal)
Slack App Token:     (get from Slack App Dashboard)
```

---

# CORE API ENDPOINTS

---

## INSTANCE MANAGEMENT

### 1. Create Instance (Multi-Channel)

**Purpose:** Create a new instance that can handle WhatsApp, Discord, Slack, or any channel

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

---

### WhatsApp Instance Request Body

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
  "is_default": false,
  "enable_auto_split": true
}
```

**WhatsApp-Specific Fields:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `evolution_url` | string | WhatsApp API gateway URL | `https://evolution-api-production-7611.up.railway.app` |
| `evolution_key` | string | API key for Evolution API | `FA758317-709D-4BB6-BA4F-987B2335036A` |
| `whatsapp_instance` | string | Instance name in Evolution API | `whatsapp-bot` |
| `session_id_prefix` | string | Prefix for session IDs | `whatsapp-bot-` |
| `webhook_base64` | boolean | Whether webhook sends base64 | `true` |
| `enable_auto_split` | boolean | Auto-split messages on `\n\n` | `true` |

**Postman Test:**
1. Method: `POST`
2. URL: `http://localhost:8882/api/v1/instances`
3. Headers: Add `x-api-key: omni-dev-key-test-2025`
4. Body (raw JSON): Copy WhatsApp request body
5. Click Send → Status `201 Created`

---

### Discord Instance Request Body

```json
{
  "name": "discord-bot",
  "channel_type": "discord",
  "discord_bot_token": "YOUR_DISCORD_BOT_TOKEN",
  "discord_client_id": "YOUR_CLIENT_ID",
  "discord_guild_id": "YOUR_GUILD_ID",
  "discord_default_channel_id": "YOUR_CHANNEL_ID",
  "discord_voice_enabled": true,
  "discord_slash_commands_enabled": true,
  "agent_api_url": "http://localhost:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "agent_timeout": 60,
  "is_default": false
}
```

**Discord-Specific Fields:**

| Field | Type | Purpose | How to Get |
|-------|------|---------|-----------|
| `discord_bot_token` | string | Bot authentication token | [Discord Developer Portal](https://discord.com/developers/applications) → Bot → Copy Token |
| `discord_client_id` | string | Application ID | Developer Portal → General Information → Application ID |
| `discord_guild_id` | string | Server/Guild ID | Right-click server → Copy Server ID |
| `discord_default_channel_id` | string | Default text channel | Right-click channel → Copy Channel ID |
| `discord_voice_enabled` | boolean | Enable voice integration | `true` or `false` |
| `discord_slash_commands_enabled` | boolean | Enable slash commands | `true` or `false` |

**Discord IPC Architecture:**
```
Discord Bot Instance
    ↓
IPC Communication Layer (Inter-Process Communication)
    ↓
Omni Message Router
    ↓
Agent API
    ↓
Response back to Discord
```

**Postman Test:**
1. Method: `POST`
2. URL: `http://localhost:8882/api/v1/instances`
3. Headers: Add `x-api-key: omni-dev-key-test-2025`
4. Body (raw JSON): Copy Discord request body with your actual tokens
5. Click Send

**Discord Bot Setup Steps:**

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section → Click "Add Bot"
4. Copy the token (this is your `discord_bot_token`)
5. Enable these **Intents**:
   - Message Content Intent
   - Server Members Intent
   - Direct Messages Intent
6. Go to OAuth2 → URL Generator
7. Select scopes: `bot`
8. Select permissions:
   - Send Messages
   - Read Messages
   - Manage Messages
   - Embed Links
   - Attach Files
9. Copy generated URL and invite bot to your server

---

### Slack Instance Request Body (Coming Q4 2025)

```json
{
  "name": "slack-bot",
  "channel_type": "slack",
  "slack_app_token": "xapp-YOUR_APP_TOKEN",
  "slack_bot_token": "xoxb-YOUR_BOT_TOKEN",
  "slack_workspace_id": "YOUR_WORKSPACE_ID",
  "slack_default_channel": "general",
  "agent_api_url": "http://localhost:8886",
  "agent_api_key": "echo-test-key",
  "default_agent": "echo",
  "agent_timeout": 60
}
```

**Slack-Specific Fields (Future):**

| Field | Type | Purpose |
|-------|------|---------|
| `slack_app_token` | string | App-level token for socket connections |
| `slack_bot_token` | string | Bot token for API calls |
| `slack_workspace_id` | string | Workspace identifier |
| `slack_default_channel` | string | Default channel to send responses |

---

### 2. Get All Instances

**Purpose:** List all instances across all channels

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

**Response:**
```json
[
  {
    "id": 1,
    "name": "whatsapp-bot",
    "channel_type": "whatsapp",
    "is_active": true,
    "agent_api_url": "http://localhost:8886",
    "created_at": "2025-12-10T14:53:04.062339"
  },
  {
    "id": 2,
    "name": "discord-bot",
    "channel_type": "discord",
    "is_active": true,
    "agent_api_url": "http://localhost:8886",
    "created_at": "2025-12-10T15:00:00.000000"
  },
  {
    "id": 3,
    "name": "slack-bot",
    "channel_type": "slack",
    "is_active": false,
    "agent_api_url": "http://localhost:8886",
    "created_at": "2025-12-10T15:05:00.000000"
  }
]
```

**Postman Test:**
1. Method: `GET`
2. URL: `http://localhost:8882/api/v1/instances`
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Click Send

---

### 3. Get Single Instance

**Endpoint:**
```
GET /api/v1/instances/{instance_name}
```

**URL:**
```
http://localhost:8882/api/v1/instances/whatsapp-bot
```

**Response:**
```json
{
  "id": 1,
  "name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "whatsapp_instance": "whatsapp-bot",
  "agent_api_url": "http://localhost:8886",
  "is_active": true,
  "evolution_status": {
    "state": "open",
    "owner_jid": "919014456421@s.whatsapp.net",
    "profile_name": "Omni Bot"
  }
}
```

---

### 4. Update Instance

**Endpoint:**
```
PUT /api/v1/instances/{instance_name}
```

**Example: Update Discord instance with new channel**

```json
{
  "discord_default_channel_id": "NEW_CHANNEL_ID",
  "agent_timeout": 90
}
```

**Example: Update WhatsApp agent**

```json
{
  "default_agent": "my-custom-agent",
  "agent_timeout": 120
}
```

---

### 5. Delete Instance

**Endpoint:**
```
DELETE /api/v1/instances/{instance_name}
```

---

# CHANNEL-SPECIFIC ENDPOINTS

---

## WHATSAPP SPECIFIC

### 1. Get QR Code for WhatsApp Connection

**Purpose:** Generate QR code to authenticate WhatsApp session

**Endpoint:**
```
GET /api/v1/instances/{instance_name}/qr
```

**URL:**
```
http://localhost:8882/api/v1/instances/whatsapp-bot/qr
```

**Headers:**
```json
{
  "x-api-key": "omni-dev-key-test-2025"
}
```

**Response:**
```json
{
  "qr": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQMA...",
  "instance_name": "whatsapp-bot",
  "status": "WAITING",
  "expires_in": 60
}
```

**How to Use:**
1. Copy the `qr` value (base64-encoded image)
2. Open in browser or WhatsApp Web
3. Scan with WhatsApp phone → Connected!

**Postman Test:**
1. Method: `GET`
2. URL: `http://localhost:8882/api/v1/instances/whatsapp-bot/qr`
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Copy response, save base64 as image and scan

---

### 2. WhatsApp Message Webhook

**Endpoint:**
```
POST /webhook/evolution/{instance_name}
```

**URL:**
```
http://localhost:8882/webhook/evolution/whatsapp-bot
```

**Request Body:**
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
    "conversation": "Hello! This is a test message."
  }
}
```

**Postman Test:**
1. Method: `POST`
2. URL: `http://localhost:8882/webhook/evolution/whatsapp-bot`
3. Headers: `Content-Type: application/json`
4. Body: Copy request body above
5. Click Send → Status `200 OK`

---

### 3. Send WhatsApp Text Message

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-text
```

**Request:**
```json
{
  "phone": "919391189719",
  "text": "Hello Pavan! This is a test message.",
  "quoted_message_id": null
}
```

**Response:**
```json
{
  "status": "sent",
  "message_id": "3EB0612AFB2310B9E050",
  "timestamp": "2025-12-11T10:42:32.500000"
}
```

---

### 4. Send WhatsApp Media (Image, Video, Document)

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-media
```

**Request:**
```json
{
  "phone": "919391189719",
  "media_type": "image",
  "media_url": "https://example.com/image.jpg",
  "caption": "Check out this image!"
}
```

**Media Types:**
| Type | Format | Example |
|------|--------|---------|
| `image` | JPG, PNG | `https://example.com/photo.jpg` |
| `video` | MP4, MOV | `https://example.com/video.mp4` |
| `audio` | MP3, WAV, OGG | `https://example.com/audio.mp3` |
| `document` | PDF, DOC, XLS | `https://example.com/file.pdf` |

---

### 5. Send WhatsApp Audio/Voice Note

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-audio
```

**Request:**
```json
{
  "phone": "919391189719",
  "audio_url": "https://example.com/voice.mp3"
}
```

---

### 6. Send WhatsApp Reaction/Emoji

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-reaction
```

**Request:**
```json
{
  "phone": "919391189719",
  "message_id": "3EB0612AFB2310B9E050",
  "emoji": "👍"
}
```

---

### 7. Check WhatsApp Connection Status

**Endpoint:**
```
GET /api/v1/instances/{instance_name}/status
```

**Response:**
```json
{
  "instance_name": "whatsapp-bot",
  "state": "open",
  "connected": true,
  "profile_name": "Omni Bot",
  "owner_jid": "919014456421@s.whatsapp.net",
  "last_updated": "2025-12-11T10:42:32.500000"
}
```

---

### 8. Restart WhatsApp Connection

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/restart
```

**Response:**
```json
{
  "status": "restarting",
  "message": "WhatsApp connection restarting",
  "instance_name": "whatsapp-bot"
}
```

---

### 9. Logout WhatsApp Session

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/logout
```

**Response:**
```json
{
  "status": "logged_out",
  "message": "WhatsApp session logged out",
  "instance_name": "whatsapp-bot"
}
```

---

## DISCORD SPECIFIC

### 1. Discord Message Webhook (Automatic)

When Discord receives a message, it's automatically routed to Omni via IPC.

**No manual webhook needed** - Discord bot is managed through the IPC layer.

---

### 2. Send Discord Text Message

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-text
```

**Request:**
```json
{
  "channel_id": "123456789",
  "text": "Hello Discord! This is a test message."
}
```

**Response:**
```json
{
  "status": "sent",
  "message_id": "987654321",
  "channel_id": "123456789"
}
```

---

### 3. Send Discord Embed (Rich Message)

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-embed
```

**Request:**
```json
{
  "channel_id": "123456789",
  "embed": {
    "title": "Test Embed",
    "description": "This is an embedded message",
    "color": 5814783,
    "fields": [
      {
        "name": "Field 1",
        "value": "Value 1",
        "inline": false
      }
    ],
    "image": {
      "url": "https://example.com/image.jpg"
    }
  }
}
```

**Color Options:**
- Red: `15158332`
- Green: `5814783`
- Blue: `3447003`
- Yellow: `15908544`
- Purple: `9807270`

---

### 4. Send Discord Reaction

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-reaction
```

**Request:**
```json
{
  "channel_id": "123456789",
  "message_id": "987654321",
  "emoji": "👍"
}
```

---

### 5. Send Discord File/Attachment

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-file
```

**Request:**
```json
{
  "channel_id": "123456789",
  "file_url": "https://example.com/document.pdf",
  "file_name": "document.pdf"
}
```

---

### 6. Get Discord Bot Status

**Endpoint:**
```
GET /api/v1/instances/{instance_name}/status
```

**Response:**
```json
{
  "instance_name": "discord-bot",
  "bot_id": "123456789",
  "bot_name": "Omni Bot",
  "guilds": 5,
  "users": 250,
  "status": "online"
}
```

---

## SLACK SPECIFIC (Coming Q4 2025)

### 1. Slack Message Webhook

**Endpoint:**
```
POST /webhook/slack/{instance_name}
```

**Request:**
```json
{
  "event": {
    "type": "message",
    "user": "U12345678",
    "text": "Hello Slack!",
    "channel": "C12345678",
    "ts": "1234567890.123456"
  }
}
```

---

### 2. Send Slack Message

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-text
```

**Request:**
```json
{
  "channel": "general",
  "text": "Hello from Omni!"
}
```

---

### 3. Send Slack Thread Reply

**Endpoint:**
```
POST /api/v1/instances/{instance_name}/send-thread-reply
```

**Request:**
```json
{
  "channel": "general",
  "thread_ts": "1234567890.123456",
  "text": "Reply to thread"
}
```

---

# TRACE & MONITORING

### 1. Get All Traces

**Endpoint:**
```
GET /api/v1/traces
```

**Query Parameters:**
```
?limit=50&offset=0&status=completed&instance=whatsapp-bot&channel_type=whatsapp
```

**Response:**
```json
[
  {
    "id": "f86e4bc9-14b4-425f-9a3a-d6c027f8ff90",
    "instance_name": "whatsapp-bot",
    "channel_type": "whatsapp",
    "phone_number": "919391189719",
    "status": "completed",
    "message_text": "Hello from Postman!",
    "agent_response": "[Echo from whatsapp] [Pavan]: Hello from Postman!",
    "evolution_success": true,
    "processing_time_ms": 2500,
    "created_at": "2025-12-11T10:42:30.000000"
  }
]
```

**Trace Status Values:**

| Status | Meaning |
|--------|---------|
| `received` | Webhook received the message |
| `processing` | Message queued for processing |
| `agent_called` | Agent API called |
| `completed` | Successfully sent to channel |
| `failed` | Error during processing |

**Postman Test:**
1. Method: `GET`
2. URL: `http://localhost:8882/api/v1/traces`
3. Headers: `x-api-key: omni-dev-key-test-2025`
4. Click Send

---

### 2. Get Single Trace

**Endpoint:**
```
GET /api/v1/traces/{trace_id}
```

**Response:**
```json
{
  "id": "f86e4bc9-14b4-425f-9a3a-d6c027f8ff90",
  "instance_name": "whatsapp-bot",
  "channel_type": "whatsapp",
  "phone_number": "919391189719",
  "contact_name": "Pavan",
  "status": "completed",
  "message_text": "Hello from Postman!",
  "agent_name": "echo",
  "agent_response": "[Echo from whatsapp] [Pavan]: Hello from Postman!",
  "response_status": 200,
  "success": true,
  "processing_time_ms": 2500,
  "created_at": "2025-12-11T10:42:30.000000",
  "completed_at": "2025-12-11T10:42:32.500000"
}
```

---

### 3. Get Traces by Channel

**Query Parameters:**
```
GET /api/v1/traces?channel_type=whatsapp
GET /api/v1/traces?channel_type=discord
GET /api/v1/traces?channel_type=slack
```

---

# AGENT API

### 1. Chat Endpoint

**Endpoint:**
```
POST /api/agent/chat
```

**URL:**
```
http://localhost:8886/api/agent/chat
```

**Request:**
```json
{
  "user_id": "d3b657af-d006-5e44-915b-dd08353f1b38",
  "session_id": "2781b4f5-c907-559c-9967-cc296d2c1a0a",
  "session_name": "whatsapp-bot_919391189719",
  "message": "[Pavan]: Hello agent!",
  "message_type": "text",
  "session_origin": "whatsapp",
  "user": {
    "phone_number": "+919391189719",
    "email": null,
    "user_data": null
  }
}
```

**Response:**
```json
{
  "text": "[Echo from whatsapp] [Pavan]: Hello agent!",
  "message": "[Echo from whatsapp] [Pavan]: Hello agent!",
  "success": true,
  "session_id": "unknown"
}
```

---

### 2. Health Check

**Endpoint:**
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "echo-agent"
}
```

---

# ADVANCED FEATURES

---

## MCP Server Integration

**What is MCP?** Model Context Protocol - allows Claude, Cursor, and other tools to control Omni

### Available MCP Tools

1. **manage_instances** - Create, list, update, delete instances
2. **send_message** - Send messages across all channels
3. **manage_traces** - View message history and analytics
4. **manage_profiles** - Update user profiles

### Usage from Claude Code

```
"Create a new WhatsApp instance named 'support-bot'"
→ Creates whatsapp-bot instance automatically

"Send a WhatsApp message to +919391189719: Hello there!"
→ Sends message via active instance

"Show me all failed messages from today"
→ Retrieves traces with status=failed

"Get Discord bot status for discord-bot"
→ Checks bot connection status
```

---

## Complete End-to-End Test Flow

### Scenario 1: Test WhatsApp Webhook

**Steps:**
1. Create WhatsApp instance
2. Get QR code and scan
3. Send test message via webhook
4. Check trace → Status should be `completed`
5. Verify message in logs

---

### Scenario 2: Test Discord Bot

**Steps:**
1. Create Discord instance with bot token
2. Add bot to server
3. Send test message to channel
4. Check trace → Status should be `completed`
5. Verify message in Discord channel

---

### Scenario 3: Test Multi-Channel

**Steps:**
1. Create WhatsApp instance
2. Create Discord instance
3. Send messages to both
4. Check traces for both channels
5. Verify each instance processes independently

---

## Performance Benchmarks

| Operation | Expected Time | Status |
|-----------|---------------|--------|
| Create Instance | < 500ms | ✅ |
| Webhook Response | < 100ms | ✅ |
| Agent Processing | 100-500ms | ✅ |
| Send to Channel | < 2000ms | ✅ |
| Total End-to-End | 1-3 seconds | ✅ |

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Webhook returns 404 | Instance doesn't exist | Create instance first |
| Trace stuck at `agent_called` | Agent timeout | Check agent is running |
| Discord bot not responding | Wrong token or permissions | Verify bot token and scopes |
| WhatsApp not connected | QR not scanned | Rescan QR code |
| Message not sent | Agent API error | Check agent logs |

---

## Summary Checklist

- ✅ WhatsApp instance creation & testing
- ✅ Discord instance creation & testing
- ✅ Slack support (coming Q4 2025)
- ✅ Multi-channel message routing
- ✅ Complete trace tracking
- ✅ Agent API integration
- ✅ MCP server features
- ✅ Advanced testing procedures

**All systems production-ready!** 🚀

