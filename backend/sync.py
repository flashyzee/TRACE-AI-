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

    # After pushing local -> cloud, pull any cloud changes -> local
    try:
        reconcile_result = reconcile_from_cloud()
        result["reconciled"] = {
            "cases_pulled": reconcile_result["cases_pulled"],
            "decisions_pulled": reconcile_result["decisions_pulled"],
            "conflicts": reconcile_result["conflicts"],
        }
    except Exception as e:
        result["errors"].append(f"reconciliation: {e}")

    return result


def reconcile_from_cloud():
    """
    Pull cloud records that are newer than their local counterparts.
    Uses last-write-wins (timestamp comparison) for conflict resolution.
    Returns: {"cases_pulled": int, "decisions_pulled": int, "conflicts": int, "errors": []}
    """
    init_cloud_db()
    result = {"cases_pulled": 0, "decisions_pulled": 0, "conflicts": 0, "errors": []}

    # ── Reconcile cases ──────────────────────────────────────────────────
    try:
        cloud = sqlite3.connect(_CLOUD_DB)
        cloud.row_factory = sqlite3.Row
        local_dash = sqlite3.connect(_DASHBOARD_DB)
        local_dash.row_factory = sqlite3.Row

        cloud_cases = cloud.execute("SELECT * FROM cases_cloud").fetchall()
        for crow in cloud_cases:
            cr = dict(crow)
            local_row = local_dash.execute(
                "SELECT * FROM cases WHERE session_id = ?",
                (cr["session_id"],),
            ).fetchone()

            if local_row is None:
                # New record from cloud -- insert locally
                try:
                    local_dash.execute("""
                        INSERT INTO cases
                        (session_id, fault_code, fault_name, vehicle_id, mileage,
                         symptoms, top_cause, confidence, updated_confidence,
                         estimated_cost, urgency, escalation_reason, evidence_json,
                         status, approved_by, reviewer_notes, repair_steps_json,
                         created_at, decided_at, sync_status)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        cr["session_id"], cr.get("fault_code"), cr.get("fault_name"),
                        cr.get("vehicle_id"), cr.get("mileage"), cr.get("symptoms"),
                        cr.get("top_cause"), cr.get("confidence"),
                        cr.get("updated_confidence"), cr.get("estimated_cost"),
                        cr.get("urgency"), cr.get("escalation_reason"),
                        cr.get("evidence_json"), cr.get("status"),
                        cr.get("approved_by"), cr.get("reviewer_notes"),
                        cr.get("repair_steps_json"), cr.get("created_at"),
                        cr.get("decided_at"), "synced",
                    ))
                    result["cases_pulled"] += 1
                except Exception as e:
                    result["errors"].append(f"case insert {cr['session_id']}: {e}")
            else:
                # Record exists locally -- last-write-wins by timestamp
                lr = dict(local_row)
                cloud_ts = cr.get("synced_at") or cr.get("decided_at") or cr.get("created_at") or ""
                local_ts = lr.get("decided_at") or lr.get("created_at") or ""

                if cloud_ts > local_ts:
                    try:
                        local_dash.execute("""
                            UPDATE cases SET
                                status=?, approved_by=?, reviewer_notes=?,
                                repair_steps_json=?, decided_at=?, sync_status='synced'
                            WHERE session_id=?
                        """, (
                            cr.get("status"), cr.get("approved_by"),
                            cr.get("reviewer_notes"), cr.get("repair_steps_json"),
                            cr.get("decided_at"), cr["session_id"],
                        ))
                        result["cases_pulled"] += 1
                        result["conflicts"] += 1
                    except Exception as e:
                        result["errors"].append(f"case update {cr['session_id']}: {e}")

        local_dash.commit()
        cloud.close()
        local_dash.close()
    except Exception as e:
        result["errors"].append(f"cases reconcile: {e}")

    # ── Reconcile decision_log ───────────────────────────────────────────
    try:
        cloud = sqlite3.connect(_CLOUD_DB)
        cloud.row_factory = sqlite3.Row
        local_ai = sqlite3.connect(_TRACE_AI_DB)

        cloud_decisions = cloud.execute("SELECT * FROM decision_log_cloud").fetchall()
        for crow in cloud_decisions:
            cr = dict(crow)
            existing = local_ai.execute(
                "SELECT id FROM decision_log WHERE session_id = ? AND action = ? AND timestamp = ?",
                (cr["session_id"], cr["action"], cr["timestamp"]),
            ).fetchone()

            if existing is None:
                try:
                    local_ai.execute("""
                        INSERT INTO decision_log
                        (session_id, action, confidence, timestamp, sync_status)
                        VALUES (?,?,?,?,?)
                    """, (
                        cr["session_id"], cr["action"], cr["confidence"],
                        cr["timestamp"], "synced",
                    ))
                    result["decisions_pulled"] += 1
                except Exception as e:
                    result["errors"].append(f"decision insert: {e}")

        local_ai.commit()
        cloud.close()
        local_ai.close()
    except Exception as e:
        result["errors"].append(f"decisions reconcile: {e}")

    # Log the reconciliation event
    total = result["cases_pulled"] + result["decisions_pulled"]
    if total > 0 or result["errors"]:
        log_sync_event(
            "reconcile_from_cloud",
            cases_synced=result["cases_pulled"],
            decisions_synced=result["decisions_pulled"],
            errors_count=len(result["errors"]),
            details=json.dumps({
                "conflicts_resolved": result["conflicts"],
                "errors": result["errors"][:5],
            }),
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
