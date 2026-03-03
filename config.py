import logging
import json

logging.basicConfig(
    filename="decision_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)


def audit_log(entry: dict):
    logging.info(json.dumps(entry))