import sqlite3

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

cursor.execute('SELECT name, is_active, discord_bot_token FROM instance_configs WHERE name="discordtesting01"')
result = cursor.fetchone()

if result:
    name, is_active, token = result
    print(f'Instance: {name}')
    print(f'Is Active: {is_active}')
    print(f'Has Token: {"YES" if token else "NO"}')
else:
    print('Instance not found')

conn.close()
