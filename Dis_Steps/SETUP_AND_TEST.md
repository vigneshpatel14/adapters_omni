# Discord Integration - Setup & Testing Guide

**No theory. Just practical steps.**

---

## PART 1: DISCORD BOT SETUP

### Step 1: Create Discord Application

1. Go to: **https://discord.com/developers/applications**
2. Click **"New Application"** button (top right)
3. Name it: `Automagik-Omni-Test`
4. Click **"Create"**

### Step 2: Get Bot Token

1. In your application, click **"Bot"** (left sidebar)
2. Click **"Add Bot"** button
3. Under **TOKEN**, click **"Copy"** button
4. Save this token somewhere (you'll need it)

**Your Bot Token looks like:**
```
YOUR_DISCORD_BOT_TOKEN_HERE
```

### Step 3: Enable Message Content Intent

1. Still in Bot section, scroll down to **"GATEWAY INTENTS"**
2. Toggle ON these intents:
   - ✅ **Message Content Intent**
   - ✅ **Guild Messages**
   - ✅ **Direct Messages**

3. Click **"Save Changes"**

### Step 4: Add Bot to Your Server

1. Click **"OAuth2"** (left sidebar)
2. Click **"URL Generator"** (sub-section)
3. Select these **SCOPES**:
   - ✅ `bot`
   - ✅ `applications.commands`

4. Select these **PERMISSIONS**:
   - ✅ `Send Messages`
   - ✅ `Read Messages/View Channels`
   - ✅ `Manage Messages`
   - ✅ `Add Reactions`
   - ✅ `Read Message History`

5. Copy the generated URL
6. Open it in a new tab
7. Select your test Discord server
8. Click **"Authorize"**

**Result:** Your bot is now in your Discord server

### Step 5: Get Your Guild ID (Server ID)

1. Go to your Discord server
2. Right-click on server name
3. Click **"Copy Server ID"**
4. Save this (looks like: `123456789012345678`)

### Step 6: Get a Channel ID

1. In Discord, go to any text channel in your server
2. Right-click on channel name
3. Click **"Copy Channel ID"**
4. Save this (looks like: `987654321098765432`)

**Summary of what you have:**
- Bot Token: `MTk4NjIyNDgzNDU1OTIyNjU2...`
- Guild ID: `123456789012345678`
- Channel ID: `987654321098765432`

---

## PART 2: CREATE OMNI INSTANCE (First Time Setup)

### Step 1: Check Omni is Running

```bash
# Open PowerShell in your Omni folder
cd c:\Automagic_Omni

# Check if services are running
pm2 status
```

**You should see:**
```
│ 0 │ automagik-omni     │ online │
│ 1 │ automagik-omni-discord │ online │
```

If not running:
```bash
pm2 start ecosystem.config.js
```

### Step 2: Create Discord Instance via API

**Using PowerShell:**

```powershell
$headers = @{
    "x-api-key" = "your-api-key-here"
    "Content-Type" = "application/json"
}

$body = @{
    name = "test-discord-bot"
    channel_type = "discord"
    discord_bot_token = "YOUR_BOT_TOKEN_HERE"
    discord_client_id = "YOUR_CLIENT_ID"
    discord_guild_id = "YOUR_GUILD_ID"
    discord_default_channel_id = "YOUR_CHANNEL_ID"
    agent_api_url = "http://localhost:8886"
    agent_api_key = "test-key"
} | ConvertTo-Json

$response = Invoke-WebRequest `
    -Uri "http://localhost:8882/api/v1/instances" `
    -Method POST `
    -Headers $headers `
    -Body $body

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

**Or using curl (simpler):**

```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-discord-bot",
    "channel_type": "discord",
    "discord_bot_token": "YOUR_BOT_TOKEN_HERE",
    "discord_client_id": "YOUR_CLIENT_ID",
    "discord_guild_id": "YOUR_GUILD_ID",
    "discord_default_channel_id": "YOUR_CHANNEL_ID",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "test-key"
  }'
```

**Expected Response:**
```json
{
  "id": "instance-123",
  "name": "test-discord-bot",
  "channel_type": "discord",
  "status": "created"
}
```

### Step 3: Check Instance Status

```bash
curl -X GET http://localhost:8882/api/v1/instances/test-discord-bot/status \
  -H "x-api-key: your-api-key-here"
```

**Expected Response:**
```json
{
  "status": "online",
  "bot_user_id": "123456789",
  "bot_user_name": "Automagik-Omni-Test",
  "guild_id": "YOUR_GUILD_ID",
  "uptime_seconds": 45
}
```

**If status is "offline":**
- Check Discord bot token is correct
- Check guild ID and channel ID are correct
- Check bot has permissions in server

---

## PART 3: TESTING FROM DISCORD

### Step 1: Send Message in Discord

1. Open your Discord server
2. Go to the channel where bot was added
3. Type: `Hello bot, what is 2+2?`
4. Send the message

### Step 2: What Should Happen?

The bot should:
- ✅ Receive the message
- ✅ Log it in Omni
- ✅ Send to your agent endpoint
- ✅ Get response back
- ✅ Reply in the same Discord channel

**Expected Discord Response:**
Something like: `2+2 equals 4.`

### Step 3: Check Logs

```bash
# View Discord service logs
pm2 logs automagik-omni-discord

# Look for lines like:
# [INFO] Message received from user: Hello bot, what is 2+2?
# [INFO] Response sent: 2+2 equals 4.
```

### Step 4: Verify Message Was Traced

```bash
# Check Omni logs
pm2 logs automagik-omni

# Look for trace entries showing Discord message flow
```

### Step 5: Send Different Types of Messages to Test

**Test 1: Simple question**
```
Hi, what's your name?
```

**Test 2: Multi-word message**
```
Tell me a joke about programming
```

**Test 3: Special characters**
```
How do I use @mentions and #hashtags?
```

---

## PART 4: UNDERSTANDING DISCORD MESSAGE INGESTION

### Important: How Discord Messages Are Different

Discord uses a **completely different architecture** than WhatsApp for receiving messages:

| Channel | Method | Endpoint |
|---------|--------|----------|
| **WhatsApp** | HTTP Webhook | `POST /webhook/evolution/{instance_name}` |
| **Discord** | Bot Gateway | WebSocket (NO HTTP ENDPOINT) |

**Discord messages do NOT use HTTP endpoints** like WhatsApp does. Instead:

1. **Discord Gateway Connection** - Bot connects via WebSocket using your bot token
2. **Event-Based** - Discord sends events directly to the running bot instance
3. **On_Message Handler** - Bot receives events through `on_message()` callback
4. **Message Router** - Events are routed to your agent automatically

### Message Flow Diagram

```
Discord Server
    ↓
Discord Gateway (WebSocket)
    ↓
Running Bot Instance (in automagik-omni-discord service)
    ↓
on_message() Event Handler
    ↓
Message Router
    ↓
Leo Agent API
    ↓
Response sent back to Discord
```

### Why There's No `/receive-message` Endpoint

❌ **This endpoint does NOT exist and should NOT be used:**
```
POST /api/v1/instances/test-discord-bot/receive-message  [404 ERROR]
```

**Why?** Discord works through the bot gateway, not HTTP webhooks. The bot continuously listens for messages on Discord's servers, not through your API.

---

## PART 5: TESTING FROM DISCORD DIRECTLY

### The Best Way to Test: Send Actual Discord Messages

Once your bot is running and connected to your Discord server:

1. Open your Discord server
2. Go to the text channel where the bot was added
3. Send a message: `"Hello bot, can you help me?"`
4. The bot should respond automatically

**Check the logs to see message flow:**

```bash
# Watch Discord service logs
pm2 logs automagik-omni-discord

# You should see:
# [INFO] Message received from user: Hello bot, can you help me?
# [INFO] Routing to agent...
# [INFO] Response received from agent
# [INFO] Message sent to Discord
```

---

## PART 6: ADVANCED TESTING (If No Real Discord Token)

**If you want to test the message routing WITHOUT a real Discord bot token:**

### Option A: Use a Mock Token (Service Will Show "Offline")

This is what we did earlier with `YOUR_DISCORD_BOT_TOKEN_HERE`. The system will track it but won't connect.

### Option B: Direct Database Testing

Inject test messages directly into the trace system (advanced):

```python
# This tests the message routing logic without Discord
python scripts/test_discord_message_routing.py
```

### Option C: Use a Real Discord Token

The most reliable way is to:

1. Create a real Discord bot in Developer Portal
2. Get the actual bot token
3. Update your instance with: `PATCH /api/v1/instances/test-discord-bot`
4. Restart: `pm2 restart automagik-omni-discord`
5. Send real messages from Discord

---

## PART 7: POSTMAN TESTING (For WhatsApp-Style Testing)

If you want to test using Postman like WhatsApp, use this WhatsApp endpoint instead:

```
POST /webhook/evolution/{instance_name}
```

**For Discord:** The bot handles all message reception automatically through Discord's gateway, so Postman testing isn't applicable. Discord messages come through the gateway connection, not HTTP webhooks.

---

## Troubleshooting Discord Connection Issues

Click **"Send"** button

### Step 6: Check Response

**You should get:**
```json
{
  "status": "received",
  "message_id": "msg-123456",
  "processing": true
}
```

### Step 7: Check Omni Logs

```bash
pm2 logs automagik-omni
```

**Look for:**
- `[INFO] Message received from TestUser: What is the capital of France?`
- `[INFO] Calling agent endpoint...`
- `[INFO] Agent response: The capital of France is Paris.`

### Step 8: Verify Discord Response

The bot should now send response to Discord channel:
- Go to Discord
- Check the channel
- You should see bot's response: `The capital of France is Paris.`

### Step 9: Test Different Scenarios with Postman

**Test 1: Message with mentions**
```json
{
  "message": {
    "id": "msg-124",
    "author": {"id": "user-789", "name": "TestUser"},
    "channel": {"id": "YOUR_CHANNEL_ID"},
    "guild": {"id": "YOUR_GUILD_ID"},
    "content": "@everyone hello from Postman",
    "timestamp": "2025-12-19T10:31:00Z"
  }
}
```

**Test 2: Message with special characters**
```json
{
  "message": {
    "id": "msg-125",
    "author": {"id": "user-789", "name": "TestUser"},
    "channel": {"id": "YOUR_CHANNEL_ID"},
    "guild": {"id": "YOUR_GUILD_ID"},
    "content": "Test: !@#$%^&*() special chars",
    "timestamp": "2025-12-19T10:32:00Z"
  }
}
```

**Test 3: Long message**
```json
{
  "message": {
    "id": "msg-126",
    "author": {"id": "user-789", "name": "TestUser"},
    "channel": {"id": "YOUR_CHANNEL_ID"},
    "guild": {"id": "YOUR_GUILD_ID"},
    "content": "This is a very long message from Postman to test if the message splitting works correctly when the response is longer than 2000 characters which is Discord's limit. This is a very long message from Postman to test if the message splitting works correctly when the response is longer than 2000 characters which is Discord's limit.",
    "timestamp": "2025-12-19T10:33:00Z"
  }
}
```

---

## Troubleshooting Discord Connection Issues

### Problem: Bot not appearing in Discord

**Solution:**
1. Check bot token is correct (copy/paste again)
2. Check OAuth2 scopes include `bot`
3. Check bot permissions include `Send Messages`
4. Recreate bot if needed

### Problem: Discord service shows offline

**Solution:**
```bash
# Check service status
pm2 status

# Restart Discord service
pm2 restart automagik-omni-discord

# Check logs
pm2 logs automagik-omni-discord
```

**If still showing "Found 0 Discord instances":**
- Check that `discord_bot_token` is a REAL Discord bot token (not placeholder)
- Real tokens look like: `YOUR_REAL_DISCORD_BOT_TOKEN_HERE`
- Placeholder text like `YOUR_DISCORD_BOT_TOKEN_HERE` won't work
- Update the token via PATCH if needed

### Problem: Message sent from Discord but no response

**Solution:**
1. Check agent endpoint is running:
   ```bash
   curl http://localhost:8886/health
   ```

2. Check agent API key is correct in instance creation

3. Check logs:
   ```bash
   pm2 logs automagik-omni
   pm2 logs automagik-omni-discord
   ```

### Problem: 404 Error on `/receive-message` endpoint

**Solution:**
- ✅ This is normal! Discord does NOT use HTTP endpoints
- ✅ Discord messages come through the bot gateway connection
- ✅ You don't need to POST to any endpoint for Discord
- ✅ The bot automatically receives messages when connected to Discord gateway
- ❌ Don't try to use `/receive-message` - it doesn't exist for Discord
- ✅ For WhatsApp, use: `POST /webhook/evolution/{instance_name}`

---

## PART 8: MESSAGE FLOW SUMMARY

### Discord Message Flow (How It Actually Works):

```
Discord Server
    ↓ (WebSocket Gateway)
Running Discord Bot Process
    ↓ (on_message event)
Message Router
    ↓ (HTTP POST)
Agent API (Leo)
    ↓ (Response)
Message Router
    ↓ (discord.py send)
Discord Channel
```

### What NOT to do:

❌ Don't send POST requests to `/receive-message` for Discord  
❌ Don't expect HTTP webhooks like WhatsApp  
❌ Don't use a placeholder bot token  

### What TO do:

✅ Use a real Discord bot token  
✅ Let the bot connect to Discord gateway automatically  
✅ Send messages in Discord - bot listens continuously  
✅ Let the routing happen automatically  

---

## PART 9: VERIFICATION CHECKLIST

After setting up, verify these items:

### Bot Setup:
- [ ] Discord application created
- [ ] Bot token copied
- [ ] Message Content Intent enabled
- [ ] Bot added to server via OAuth2
- [ ] Guild ID and Channel ID obtained

### Instance Creation:
- [ ] Instance created via API
- [ ] Instance shows `channel_type: "discord"`
- [ ] Instance shows `status: "online"`
- [ ] Discord service logs show bot connected

### Message Testing:
- [ ] Sent message in Discord channel
- [ ] Bot received and processed message
- [ ] Agent returned response
- [ ] Bot replied in Discord channel
- [ ] Message logged in Omni traces

### Logs Check:
- [ ] `pm2 logs automagik-omni-discord` shows messages received
- [ ] `pm2 logs automagik-omni` shows routing happening
- [ ] No errors in either log

---

## FAQ

**Q: Why don't I POST to an endpoint for Discord like WhatsApp?**  
A: Discord works differently. Your bot stays connected to Discord's gateway via WebSocket. It continuously listens for messages. WhatsApp uses webhooks because it's API-based, but Discord's bot model is event-driven.

**Q: What if I don't have a real Discord server?**  
A: Create a free Discord server for testing, or ask to join an existing test server.

**Q: Can I test with a fake bot token?**  
A: You can create the instance with a fake token, but the Discord service won't start the bot. Use a real token to test the full flow.

**Q: What's the difference between bot token and webhook?**  
A: Bot token is used for bot authentication. Webhooks are a separate feature for sending messages TO Discord (not receiving). Your bot uses the token to connect and listen for messages.

**Q: Does the bot need to be online all the time?**  
A: Yes, the Discord bot process needs to keep running to listen for messages. That's why it's in PM2 - it auto-restarts if it crashes.

---
- [ ] Postman got 200 response
- [ ] Message appeared in Omni logs
- [ ] Agent was called
- [ ] Response appeared in Discord

### If anything fails, check:
- [ ] Logs: `pm2 logs automagik-omni`
- [ ] Logs: `pm2 logs automagik-omni-discord`
- [ ] Instance status: `curl http://localhost:8882/api/v1/instances/test-discord-bot/status`
- [ ] Agent health: `curl http://localhost:8886/health`

---

## PART 8: NEXT STEPS

Once everything works:

1. **Create more test instances** with different configurations
2. **Test with real Discord workflows** (reactions, edits, deletes)
3. **Test with multiple messages** simultaneously
4. **Test error handling** (invalid input, timeouts)
5. **Monitor performance** (response time, memory usage)

---

## QUICK REFERENCE COMMANDS

**List all instances:**
```bash
curl http://localhost:8882/api/v1/instances -H "x-api-key: your-api-key"
```

**Get instance status:**
```bash
curl http://localhost:8882/api/v1/instances/test-discord-bot/status -H "x-api-key: your-api-key"
```

**Delete instance:**
```bash
curl -X DELETE http://localhost:8882/api/v1/instances/test-discord-bot -H "x-api-key: your-api-key"
```

**View logs:**
```bash
pm2 logs automagik-omni
pm2 logs automagik-omni-discord
```

**Restart services:**
```bash
pm2 restart ecosystem.config.js
```

**Stop services:**
```bash
pm2 stop ecosystem.config.js
```

---

**That's it. Follow these steps and Discord will work.**
