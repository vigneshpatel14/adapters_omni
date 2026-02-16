import sqlite3

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

# Check the Discord instance
cursor.execute('''
    SELECT name, discord_bot_token 
    FROM instance_configs 
    WHERE name='discordtesting01'
''')

result = cursor.fetchone()
if result:
    name, token = result
    print(f'Instance: {name}')
    print(f'Token stored: {"YES" if token else "NO"}')
    if token:
        print(f'Token preview: {token[:30]}...')
    else:
        print('Token preview: None')
else:
    print('Instance not found')

conn.close()
