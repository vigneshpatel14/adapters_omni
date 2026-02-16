# Discord Bot Setup - CLARIFIED 🎮

## IMPORTANT: Bot Token vs OAuth2 Redirect URI

You're confused because the guide mixes TWO different concepts. Let me clarify:

### **Bot Token** ✅ (This is what you need)
- Used for: Bot authentication to Discord
- Where you get it: Developer Portal → Your App → Bot tab → Copy Token
- What it looks like: `YOUR_DISCORD_BOT_TOKEN_HERE`
- Where you use it: Backend `.env` file or API request body
- **Status**: ✅ YOU HAVE THIS (from mobile)

### **OAuth2 Redirect URI** ❌ (You DON'T need this)
- Used for: User login/authentication (3rd party apps like "Login with Discord")
- What it is: URL where users get redirected after login
- Example: `http://yourapp.com/auth/discord/callback`
- **Status**: ❌ NOT NEEDED for a bot running locally
- **Why not needed?**: 
  - Bots don't use OAuth2 redirect URIs
  - That's only for user authentication flows
  - Your bot just needs the token to authenticate itself

---

## Why The Guide Mentioned Redirect URI

The guide was trying to cover MULTIPLE use cases:
1. ✅ **Bot Authentication** (what you need) - Just the token
2. ❌ **User Authentication** (what you DON'T need) - Needs redirect URI
3. ❌ **Web Dashboard Login** (what you DON'T need) - Needs redirect URI

**For your use case (backend bot), ignore the redirect URI section entirely.**

---

## What You ACTUALLY Need (Simplified)

```
From Discord Developer Portal:
✅ Bot Token: YOUR_DISCORD_BOT_TOKEN_HERE
✅ Client ID: YOUR_CLIENT_ID_HERE
✅ Guild ID: Your test server ID (right-click server)
✅ Channel ID: Your test channel ID (right-click channel)

That's it. You don't need anything else for localhost.
```

---

## How to Pass Token to Omni

### **Option 1: Via API Request (Recommended)** 

You already know this from Dis_Steps:

```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: omni-dev-key-test-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "discord-bot-local",
    "channel_type": "discord",
    "discord_bot_token": "YOUR_ACTUAL_TOKEN_HERE",
    "discord_client_id": "1455145225159704717",
    "discord_guild_id": "YOUR_GUILD_ID",
    "discord_default_channel_id": "YOUR_CHANNEL_ID",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "test-key"
  }'
```

✅ **This is the easiest way**

### **Option 2: Via Environment Variables** (If you need to pre-configure)

Add to `.env`:
```dotenv
DISCORD_BOT_TOKEN="YOUR_ACTUAL_TOKEN_HERE"
DISCORD_CLIENT_ID="1455145225159704717"
DISCORD_GUILD_ID="YOUR_GUILD_ID"
DISCORD_DEFAULT_CHANNEL_ID="YOUR_CHANNEL_ID"
```

Then load from code. But Option 1 is simpler.

### **Option 3: Via Frontend UI** (If you have a dashboard)

Your frontend would send a POST request like Option 1:
```javascript
async function createDiscordInstance() {
  const response = await fetch('http://localhost:8882/api/v1/instances', {
    method: 'POST',
    headers: {
      'x-api-key': 'omni-dev-key-test-2025',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'discord-bot-local',
      channel_type: 'discord',
      discord_bot_token: document.getElementById('tokenInput').value,
      discord_client_id: '1455145225159704717',
      discord_guild_id: document.getElementById('guildInput').value,
      discord_default_channel_id: document.getElementById('channelInput').value,
      agent_api_url: 'http://localhost:8886',
      agent_api_key: 'test-key'
    })
  });
  
  return await response.json();
}
```

---

## Steps for Your Local Setup

### **Step 1: Get Your IDs from Discord**

1. Open Discord
2. Right-click your test server → **Copy Server ID** (this is `guild_id`)
3. Right-click a text channel → **Copy Channel ID** (this is `default_channel_id`)
4. You already have bot token from mobile

**You now have:**
- ✅ Bot Token (from mobile)
- ✅ Client ID: `1455145225159704717` (from your message)
- ✅ Guild ID: (from step 2)
- ✅ Channel ID: (from step 3)

### **Step 2: Enable Intents** (Still required!)

Go to Developer Portal → Your App → Bot → Gateway Intents:
- ✅ Message Content Intent (required to read messages)
- ✅ Server Members Intent
- ✅ Presence Intent (optional)

**Save changes**

### **Step 3: Create Instance via API**

Open PowerShell or Postman and run:

```bash
curl -X POST http://localhost:8882/api/v1/instances \
  -H "x-api-key: omni-dev-key-test-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "omni-discord-local",
    "channel_type": "discord",
    "discord_bot_token": "YOUR_TOKEN_FROM_MOBILE",
    "discord_client_id": "1455145225159704717",
    "discord_guild_id": "YOUR_GUILD_ID",
    "discord_default_channel_id": "YOUR_CHANNEL_ID",
    "agent_api_url": "http://localhost:8886",
    "agent_api_key": "test-key"
  }'
```

### **Step 4: Check Status**

```bash
curl http://localhost:8882/api/v1/instances/omni-discord-local/status \
  -H "x-api-key: omni-dev-key-test-2025"
```

Expected response:
```json
{
  "status": "online",
  "bot_user_id": "...",
  "bot_user_name": "YourBotName",
  "guild_id": "YOUR_GUILD_ID",
  "uptime_seconds": 45
}
```

### **Step 5: Test in Discord**

Send a message in your test channel, bot should respond!

---

## Summary: What You Need vs What You Don't

### ✅ **DO NEED:**
- Bot Token (you have it)
- Client ID (you have it)
- Guild ID (get from Discord)
- Channel ID (get from Discord)
- Message Content Intent enabled
- Server Members Intent enabled

### ❌ **DON'T NEED:**
- Redirect URI (only for user login)
- Webhook setup (that's for WhatsApp)
- Public facing URL (localhost is fine)
- Any public IP or domain

---

## Why Localhost Works Fine

Your setup:
```
Discord Bot (running in automagik-omni-discord service)
    ↓ (WebSocket connection to Discord)
Discord Gateway
    ↓ (messages sent to your bot)
Your Bot Instance
    ↓ (routes to agent)
Leo Agent (http://localhost:8886)
    ↓ (responds)
Discord Bot
    ↓ (sends back to Discord)
Discord Channel
```

**No public URL needed** because:
1. Your bot initiates the WebSocket connection (outbound)
2. Discord sends messages through that same connection
3. No incoming HTTP requests needed
4. Everything is outbound from your localhost

That's why redirect URIs aren't needed!

---

## Quick Reference Commands

**List instances:**
```bash
curl http://localhost:8882/api/v1/instances -H "x-api-key: omni-dev-key-test-2025"
```

**Check Discord service status:**
```bash
pm2 status
pm2 logs automagik-omni-discord
```

**View all traces:**
```bash
curl "http://localhost:8882/api/v1/traces?instance_name=omni-discord-local" \
  -H "x-api-key: omni-dev-key-test-2025"
```

**Restart Discord service:**
```bash
pm2 restart automagik-omni-discord
```
