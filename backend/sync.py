"""
Offline sync engine for TRACE AI.
Tracks unsynced local records and pushes them to a "cloud" database on reconnect.
The "cloud" is a separate SQLite DB (data/cloud.db) simulating a remote store.
Replace _push_* functions with real Supabase calls when ready.
"""

import sqlite3
import socket
import os
import json
from datetime import datetime

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_CLOUD_DB = os.path.join(_DATA_DIR, "cloud.db")
_DASHBOARD_DB = os.path.join(_DATA_DIR, "dashboard.db")
_TRACE_AI_DB = os.path.join(_DATA_DIR, "trace_ai.db")


def check_connectivity(timeout=2):
    """Check internet connectivity by reaching Google DNS. Fast and reliable."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False


def init_cloud_db():
    """Create cloud DB tables mirroring local schema."""
    conn = sqlite3.connect(_CLOUD_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cases_cloud (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            fault_code TEXT, fault_name TEXT, vehicle_id TEXT,
            mileage INTEGER, symptoms TEXT, top_cause TEXT,
            confidence REAL, updated_confidence REAL,
            estimated_cost INTEGER, urgency TEXT,
            escalation_reason TEXT, evidence_json TEXT,
            status TEXT, approved_by TEXT, reviewer_notes TEXT,
            repair_steps_json TEXT, created_at TEXT, decided_at TEXT,
            synced_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decision_log_cloud (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT, action TEXT, confidence REAL,
            timestamp TEXT, synced_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_sync_stats():
    """Return counts of synced vs pending for UI display."""
    stats = {
        "cases_pending": 0,
        "cases_synced": 0,
        "decisions_pending": 0,
        "decisions_synced": 0,
    }

    try:
        dash = sqlite3.connect(_DASHBOARD_DB)
        stats["cases_pending"] = dash.execute(
            "SELECT COUNT(*) FROM cases WHERE sync_status = 'pending'"
        ).fetchone()[0]
        stats["cases_synced"] = dash.execute(
            "SELECT COUNT(*) FROM cases WHERE sync_status = 'synced'"
        ).fetchone()[0]
        dash.close()
    except Exception:
        pass

    try:
        ai = sqlite3.connect(_TRACE_AI_DB)
        stats["decisions_pending"] = ai.execute(
            "SELECT COUNT(*) FROM decision_log WHERE sync_status = 'pending'"
        ).fetchone()[0]
        stats["decisions_synced"] = ai.execute(
            "SELECT COUNT(*) FROM decision_log WHERE sync_status = 'synced'"
        ).fetchone()[0]
        ai.close()
    except Exception:
        pass

    return stats


def sync_to_cloud():
    """
    Push all unsynced records to cloud DB.
    Returns: {"cases_synced": int, "decisions_synced": int, "errors": []}
    """
    init_cloud_db()
    result = {"cases_synced": 0, "decisions_synced": 0, "errors": []}
    now = datetime.now().isoformat()

    # ── Sync cases ──────────────────────────────────────────────────────────
    try:
        cloud = sqlite3.connect(_CLOUD_DB)
        local_dash = sqlite3.connect(_DASHBOARD_DB)
        local_dash.row_factory = sqlite3.Row

        for row in local_dash.execute(
            "SELECT * FROM cases WHERE sync_status = 'pending'"
        ).fetchall():
            r = dict(row)
            try:
                cloud.execute("""
                    INSERT OR REPLACE INTO cases_cloud
                    (session_id, fault_code, fault_name, vehicle_id, mileage,
                     symptoms, top_cause, confidence, updated_confidence,
                     estimated_cost, urgency, escalation_reason, evidence_json,
                     status, approved_by, reviewer_notes, repair_steps_json,
                     created_at, decided_at, synced_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    r["session_id"], r["fault_code"], r.get("fault_name"),
                    r.get("vehicle_id"), r.get("mileage"), r.get("symptoms"),
                    r.get("top_cause"), r.get("confidence"),
                    r.get("updated_confidence"), r.get("estimated_cost"),
                    r.get("urgency"), r.get("escalation_reason"),
                    r.get("evidence_json"), r.get("status"),
                    r.get("approved_by"), r.get("reviewer_notes"),
                    r.get("repair_steps_json"), r.get("created_at"),
                    r.get("decided_at"), now,
                ))
                local_dash.execute(
                    "UPDATE cases SET sync_status = 'synced' WHERE id = ?",
                    (r["id"],),
                )
                result["cases_synced"] += 1
            except Exception as e:
                result["errors"].append(f"case {r.get('session_id')}: {e}")

        cloud.commit()
        local_dash.commit()
        cloud.close()
        local_dash.close()
    except Exception as e:
        result["errors"].append(f"cases sync: {e}")

    # ── Sync decision_log ───────────────────────────────────────────────────
    try:
        cloud = sqlite3.connect(_CLOUD_DB)
        local_ai = sqlite3.connect(_TRACE_AI_DB)
        local_ai.row_factory = sqlite3.Row

        for row in local_ai.execute(
            "SELECT * FROM decision_log WHERE sync_status = 'pending'"
        ).fetchall():
            r = dict(row)
            try:
                cloud.execute("""
                    INSERT INTO decision_log_cloud
                    (session_id, action, confidence, timestamp, synced_at)
                    VALUES (?,?,?,?,?)
                """, (
                    r["session_id"], r["action"], r["confidence"],
                    r["timestamp"], now,
                ))
                local_ai.execute(
                    "UPDATE decision_log SET sync_status = 'synced' WHERE id = ?",
                    (r["id"],),
                )
                result["decisions_synced"] += 1
            except Exception as e:
                result["errors"].append(f"decision {r.get('id')}: {e}")

        cloud.commit()
        local_ai.commit()
        cloud.close()
        local_ai.close()
    except Exception as e:
        result["errors"].append(f"decisions sync: {e}")

    # Log the sync event for history/audit
    total = result["cases_synced"] + result["decisions_synced"]
    if total > 0 or result["errors"]:
        log_sync_event(
            "sync_complete",
            cases_synced=result["cases_synced"],
            decisions_synced=result["decisions_synced"],
            errors_count=len(result["errors"]),
            details=json.dumps(result["errors"][:5]) if result["errors"] else "",
        )

    return result


def init_sync_history():
    """Create sync_history table in cloud DB for tracking sync events."""
    conn = sqlite3.connect(_CLOUD_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            cases_synced INTEGER DEFAULT 0,
            decisions_synced INTEGER DEFAULT 0,
            errors_count INTEGER DEFAULT 0,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_sync_event(event_type, cases_synced=0, decisions_synced=0,
                   errors_count=0, details=""):
    """Record a sync event for history/audit."""
    init_cloud_db()
    init_sync_history()
    conn = sqlite3.connect(_CLOUD_DB)
    conn.execute(
        """INSERT INTO sync_history
           (event_type, cases_synced, decisions_synced, errors_count,
            details, timestamp)
           VALUES (?,?,?,?,?,?)""",
        (event_type, cases_synced, decisions_synced, errors_count,
         details, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_sync_history(limit=10):
    """Retrieve the most recent sync events."""
    init_cloud_db()
    init_sync_history()
    conn = sqlite3.connect(_CLOUD_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM sync_history ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_last_sync_time():
    """Return ISO timestamp of the last successful sync, or None."""
    init_cloud_db()
    init_sync_history()
    conn = sqlite3.connect(_CLOUD_DB)
    row = conn.execute(
        "SELECT timestamp FROM sync_history "
        "WHERE event_type IN ('sync_complete', 'reconnect_sync') "
        "ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_pending_count():
    """Return total number of records pending sync."""
    stats = get_sync_stats()
    return stats["cases_pending"] + stats["decisions_pending"]


def format_time_ago(iso_timestamp):
    """Convert ISO timestamp to human-readable relative time."""
    if not iso_timestamp:
        return "Never"
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        delta = datetime.now() - dt
        seconds = delta.total_seconds()
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins} min ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hr ago"
        else:
            days = delta.days
            return f"{days} day(s) ago"
    except (ValueError, TypeError):
        return "Unknown"
