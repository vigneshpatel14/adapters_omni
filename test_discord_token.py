import sqlite3
import aiohttp
import asyncio
import ssl
import certifi

async def test_token():
    conn = sqlite3.connect('data/automagik-omni.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT discord_bot_token FROM instance_configs WHERE name="discordtesting01"')
    result = cursor.fetchone()
    token = result[0] if result else None
    conn.close()
    
    if not token:
        print("❌ Token not found in database!")
        return
    
    print(f"🔑 Testing token: {token[:20]}...{token[-10:]}\n")
    
    # Create SSL context that validates certificates
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    # Test 1: Check if token format is valid by getting user info
    print("🌐 Test 1: Validating token with Discord API (/users/@me)")
    try:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            headers = {'Authorization': f'Bot {token}'}
            async with session.get(
                'https://discord.com/api/v10/users/@me',
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                print(f"  Status: {response.status}")
                data = await response.json()
                
                if response.status == 200:
                    print(f"  ✅ SUCCESS! Bot is valid")
                    print(f"  Bot Name: {data.get('username')}#{data.get('discriminator')}")
                    print(f"  Bot ID: {data.get('id')}")
                    print(f"  Bot Verified: {data.get('verified')}")
                elif response.status == 401:
                    print(f"  ❌ FAILED! Token is invalid or expired")
                    print(f"  Response: {data}")
                else:
                    print(f"  ⚠️  Unexpected status: {data}")
    except Exception as e:
        print(f"  ❌ Connection error: {type(e).__name__}")
        print(f"  Details: {e}")

asyncio.run(test_token())
