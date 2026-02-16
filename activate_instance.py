import sqlite3

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

cursor.execute('UPDATE instance_configs SET is_active=1 WHERE name="discordtesting01"')
conn.commit()

print('Instance activated!')
conn.close()
