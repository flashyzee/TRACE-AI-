import sqlite3
import json
import os

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trace_ai.db")
os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Create the decision_log table with full audit trail fields
cursor.execute("""
CREATE TABLE IF NOT EXISTS decision_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id TEXT,
    session_id TEXT,
    agent_id TEXT,
    action TEXT,
    fault_code TEXT,
    inputs TEXT,
    output TEXT,
    confidence REAL,
    human_approved INTEGER,
    model_used TEXT,
    metadata TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sync_status TEXT DEFAULT 'pending'
)
""")

# Migrations for existing databases that lack newer columns
_new_columns = [
    ("log_id", "TEXT"),
    ("agent_id", "TEXT"),
    ("fault_code", "TEXT"),
    ("inputs", "TEXT"),
    ("output", "TEXT"),
    ("human_approved", "INTEGER"),
    ("model_used", "TEXT"),
    ("metadata", "TEXT"),
    ("sync_status", "TEXT DEFAULT 'pending'"),
]

for col_name, col_type in _new_columns:
    try:
        cursor.execute(f"ALTER TABLE decision_log ADD COLUMN {col_name} {col_type}")
    except sqlite3.OperationalError:
        pass  # column already exists

conn.commit()


def log_decision(
    session_id: str,
    action: str,
    confidence: float,
    agent_id: str = None,
    fault_code: str = None,
    inputs: dict = None,
    output: dict = None,
    human_approved: bool = None,
    model_used: str = None,
    metadata: dict = None,
    log_id: str = None,
):
    """Insert a structured decision log entry into the SQLite database."""
    human_val = None
    if human_approved is True:
        human_val = 1
    elif human_approved is False:
        human_val = 0

    cursor.execute(
        """INSERT INTO decision_log
           (log_id, session_id, agent_id, action, fault_code,
            inputs, output, confidence, human_approved,
            model_used, metadata, sync_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (
            log_id,
            session_id,
            agent_id,
            action,
            fault_code,
            json.dumps(inputs) if inputs else None,
            json.dumps(output) if output else None,
            confidence,
            human_val,
            model_used,
            json.dumps(metadata) if metadata else None,
        ),
    )
    conn.commit()


def get_decision_logs(session_id: str = None, agent_id: str = None):
    """Fetch decision logs with optional filtering by session or agent."""
    conn_local = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn_local.row_factory = sqlite3.Row
    query = "SELECT * FROM decision_log WHERE 1=1"
    params = []

    if session_id:
        query += " AND session_id = ?"
        params.append(session_id)
    if agent_id:
        query += " AND agent_id = ?"
        params.append(agent_id)

    query += " ORDER BY timestamp ASC"
    rows = conn_local.execute(query, params).fetchall()
    conn_local.close()

    results = []
    for row in rows:
        d = dict(row)
        # Parse JSON fields back to dicts
        for field in ("inputs", "output", "metadata"):
            if d.get(field):
                try:
                    d[field] = json.loads(d[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        # Convert human_approved int back to bool/None
        if d.get("human_approved") is None:
            pass
        elif d["human_approved"] == 1:
            d["human_approved"] = True
        else:
            d["human_approved"] = False
        results.append(d)
    return results
