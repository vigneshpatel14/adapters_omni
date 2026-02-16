#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

# Check pythonassistant instance
cursor.execute('''
    SELECT id, name, channel_type, is_active, discord_bot_token, created_at
    FROM instance_configs
    WHERE name = 'pythonassistant'
''')
result = cursor.fetchone()

if result:
    id_, name, channel_type, is_active, token, created_at = result
    print(f"Instance: {name}")
    print(f"  ID: {id_}")
    print(f"  Type: {channel_type}")
    print(f"  Active: {is_active}")
    print(f"  Token Set: {'Yes' if token else 'No'}")
    print(f"  Created: {created_at}")
else:
    print("pythonassistant instance not found")

# Check all recent instances
print("\n=== Last 5 Discord instances ===")
cursor.execute('''
    SELECT id, name, is_active, discord_bot_token
    FROM instance_configs
    WHERE channel_type = 'discord'
    ORDER BY created_at DESC
    LIMIT 5
''')
for row in cursor.fetchall():
    id_, name, is_active, token = row
    print(f"ID: {id_:2d} | Name: {name:20s} | Active: {is_active} | Token: {'Yes' if token else 'No'}")

conn.close()
