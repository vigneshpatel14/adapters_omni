#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

# Check the schema
cursor.execute("PRAGMA table_info(instance_configs)")
columns = cursor.fetchall()
print('Current columns:')
for col in columns:
    print(f'  {col[1]}: {col[2]}')

conn.close()
