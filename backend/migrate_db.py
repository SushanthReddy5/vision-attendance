import re

with open('database.py', 'r') as f:
    content = f.read()

old = '''    cursor.execute(\'\'\'
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        photo_path TEXT,
        encoding TEXT NOT NULL
    )
    \'\'\')'''

new = '''    cursor.execute(\'\'\'
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        section TEXT,
        email TEXT,
        phone TEXT,
        photo_path TEXT,
        encoding TEXT NOT NULL
    )
    \'\'\')

    # Migration: add section column if it doesn't exist (for pre-existing databases)
    cursor.execute("PRAGMA table_info(students)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if 'section' not in existing_cols:
        cursor.execute("ALTER TABLE students ADD COLUMN section TEXT")'''

if old not in content:
    print("⚠️  ZERO MATCHES — aborting, no changes made.")
else:
    content = content.replace(old, new)
    with open('database.py', 'w') as f:
        f.write(content)
    print("✅ schema + migration added")
