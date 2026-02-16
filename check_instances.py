import sqlite3

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, name, is_active, discord_bot_token 
    FROM instance_configs 
    WHERE channel_type="discord"
    ORDER BY id DESC LIMIT 5
''')

rows = cursor.fetchall()
print(f"\n📋 Discord Instances (Last 5):\n")
for row in rows:
    id_, name, is_active, token = row
    has_token = "YES" if token else "NO"
    print(f"  ID: {id_:<3} | Name: {name:<15} | is_active: {is_active} (type: {type(is_active).__name__}) | Token: {has_token}")

conn.close()
