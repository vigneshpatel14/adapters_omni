#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('./data/automagik-omni.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for table in tables:
    print(f'  - {table[0]}')
print()

# Get instances
try:
    cursor.execute('SELECT * FROM instance_config')
    print('Instances:')
    for row in cursor.fetchall():
        print(json.dumps(dict(row), indent=2, default=str))
except Exception as e:
    print(f'Error getting instances: {e}')
