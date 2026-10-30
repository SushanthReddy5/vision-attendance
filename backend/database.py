import sqlite3
import hashlib
import os

DB_FILE = "attendance.db"

def _hash_password(password: str) -> str:
    """Simple SHA-256 hash with a fixed salt prefix."""
    return hashlib.sha256(("visionattend::" + password).encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ── Students table ────────────────────────────────────────────────────────
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        section TEXT,
        email TEXT,
        phone TEXT,
        photo_path TEXT,
        photo_left_path TEXT,
        photo_right_path TEXT,
        encoding TEXT NOT NULL
    )
    ''')

    # Backward-compatible migrations for students
    cursor.execute("PRAGMA table_info(students)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    for col in ['section', 'photo_left_path', 'photo_right_path']:
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col} TEXT")

    # ── Attendance table ──────────────────────────────────────────────────────
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        timestamp DATETIME NOT NULL,
        status TEXT NOT NULL,
        confidence REAL,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')

    # ── Admin users table ─────────────────────────────────────────────────────
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'System Administrator',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Seed a default admin if none exists
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    if cursor.fetchone()[0] == 0:
        default_pw = _hash_password("admin123")
        cursor.execute('''
            INSERT INTO admin_users (username, email, name, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ("admin", "admin@vision.local", "Admin", default_pw, "System Administrator"))

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return _hash_password(password)

init_db()
