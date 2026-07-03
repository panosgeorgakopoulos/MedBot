import os
from datetime import datetime
from src.anonymize_log import redact_patient_info # reuse for GDPR

AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "audit.log")

def write_audit_log(role: str, action: str, obj_id: str, batch_id: str, quantity: int, status: str, details: str = ""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] ROLE: {role} | ACTION: {action} | OBJ: {obj_id} | BATCH: {batch_id} | QTY: {quantity} | STATUS: {status} | DETAILS: {details}\n"
    secure_entry = redact_patient_info(entry)
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(secure_entry)
