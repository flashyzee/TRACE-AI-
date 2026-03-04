# backend/logging_config.py

import logging
import json
from pathlib import Path

# Ensure log directory exists
log_file = Path(__file__).resolve().parent.parent / "data" / "decision_audit.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)

def audit_log(entry: dict):
    """
    Append a JSON-formatted audit entry to the log file.
    Each entry is timestamped automatically.
    
    Example:
        audit_log({
            "session_id": "DEMO-123456",
            "action": "triage_completed",
            "confidence": 0.95
        })
    """
    # Convert dict to JSON string for readability
    json_entry = json.dumps(entry)
    
    # Append to the log (append-only)
    logging.info(json_entry)