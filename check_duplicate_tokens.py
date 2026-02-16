import sqlite3
from collections import defaultdict

conn = sqlite3.connect('data/automagik-omni.db')
cursor = conn.cursor()

# Get all Discord instances with their tokens
cursor.execute('''
    SELECT id, name, discord_bot_token, is_active 
    FROM instance_configs 
    WHERE channel_type='discord'
    ORDER BY discord_bot_token
''')

instances = cursor.fetchall()
token_map = defaultdict(list)

print("\n" + "="*100)
print("DISCORD INSTANCES - CHECKING FOR DUPLICATE TOKENS")
print("="*100 + "\n")

for id_, name, token, is_active in instances:
    if token:
        token_short = token[:15] + "..." + token[-5:]
        token_map[token].append((id_, name, is_active))
        print(f"ID: {id_:2d} | Name: {name:25s} | Token: {token_short:30s} | Active: {is_active}")
    else:
        print(f"ID: {id_:2d} | Name: {name:25s} | Token: NULL | Active: {is_active}")

print("\n" + "="*100)
print("DUPLICATE TOKEN ANALYSIS")
print("="*100 + "\n")

duplicates_found = False
for token, instances_list in token_map.items():
    if len(instances_list) > 1:
        duplicates_found = True
        token_short = token[:15] + "..." + token[-5:]
        print(f"⚠️  DUPLICATE TOKEN: {token_short}")
        print(f"   Being used by {len(instances_list)} instances:")
        for id_, name, is_active in instances_list:
            status = "ACTIVE" if is_active else "inactive"
            print(f"      - ID {id_}: {name:25s} [{status}]")
        print()

if not duplicates_found:
    print("✅ No duplicate tokens found!")

conn.close()
