import sqlite3

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

cursor.execute('UPDATE instance_configs SET is_active=1 WHERE channel_type="discord"')
conn.commit()
rows_updated = cursor.rowcount

print(f'✅ Activated {rows_updated} Discord instances')
conn.close()
