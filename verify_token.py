import sqlite3
import sys

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

# Get the Discord instance and its token
cursor.execute('''
    SELECT id, name, discord_bot_token, discord_client_id, is_active
    FROM instance_configs 
    WHERE name='discordtesting01'
''')

result = cursor.fetchone()
if result:
    id_, name, token, client_id, is_active = result
    print(f"\n📋 Instance Details:")
    print(f"  ID: {id_}")
    print(f"  Name: {name}")
    print(f"  Is Active: {is_active}")
    print(f"  Client ID: {client_id}")
    
    if token:
        # Check token format
        print(f"\n🔑 Token Details:")
        print(f"  Length: {len(token)}")
        print(f"  Format: {token[:20]}...{token[-10:]}")
        
        # Check if token contains expected structure (should have dots for bot tokens)
        if '.' in token:
            parts = token.split('.')
            print(f"  Parts (by dots): {len(parts)} (should be 3 for bot tokens)")
            for i, part in enumerate(parts):
                print(f"    Part {i+1}: {len(part)} chars")
        else:
            print("  ⚠️ WARNING: Token doesn't contain dots - might not be valid bot token format!")
            
        # Show full token for inspection
        print(f"\n🔍 Full Token:")
        print(f"  {token}")
    else:
        print("\n❌ Token is NULL in database!")
else:
    print("❌ Instance 'discordtesting01' not found in database!")

conn.close()
