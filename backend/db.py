import sqlite3

import os

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trace_ai.db")
conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS decision_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    action TEXT,
    confidence REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sync_status TEXT DEFAULT 'pending'
)
""")

# Migration for existing databases that lack the sync_status column
try:
    cursor.execute("ALTER TABLE decision_log ADD COLUMN sync_status TEXT DEFAULT 'pending'")
except sqlite3.OperationalError:
    pass  # column already exists

conn.commit()


def log_decision(session_id: str, action: str, confidence: float):
    cursor.execute(
        "INSERT INTO decision_log (session_id, action, confidence, sync_status) VALUES (?, ?, ?, 'pending')",
        (session_id, action, confidence),
    )
    conn.commit()