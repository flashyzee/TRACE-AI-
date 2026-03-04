# backend/logging_config.py

import logging
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Ensure data directory and log file exist
_data_dir = Path(__file__).resolve().parent.parent / "data"
_data_dir.mkdir(parents=True, exist_ok=True)
LOG_FILE = _data_dir / "decision_audit.log"

# Create a dedicated logger (avoid polluting the root logger)
audit_logger = logging.getLogger("trace_audit")
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False

# Only add handler if none exist yet (prevents duplicate handlers on re-import)
if not audit_logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    # Each line is a standalone JSON object (JSON Lines format)
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    audit_logger.addHandler(file_handler)


def audit_log(entry: dict):
    """
    Append a structured JSON audit entry to the decision log file.
    Automatically adds a UTC timestamp if one is not already present.

    Example:
        audit_log({
            "session_id": "SESSION-REP-1000",
            "agent_id": "triage_agent",
            "action": "initial_triage",
            "confidence": 0.72,
            "fault_code": "P0191"
        })
    """
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()

    json_line = json.dumps(entry, default=str)
    audit_logger.info(json_line)


def read_audit_log():
    """
    Read all entries from the decision audit log file.
    Returns a list of dicts parsed from JSON Lines format.
    """
    entries = []
    if not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0:
        return entries

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries
