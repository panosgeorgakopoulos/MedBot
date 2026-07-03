import re

def redact_patient_info(text: str) -> str:
    """
    GDPR-style log redaction stub.
    Redacts names, AMKA, phone numbers, or arbitrary identifiers in text.
    """
    # Mask AMKA (11 digits)
    text = re.sub(r'\b\d{11}\b', "[REDACTED_AMKA]", text)
    
    # Mask Phone Numbers (10 digits starting with 2 or 6)
    text = re.sub(r'\b[26]\d{9}\b', "[REDACTED_PHONE]", text)
    
    # Example: mask "Ασθενής <Όνομα>"
    text = re.sub(r'(Ασθενής\s+)([Α-Ωα-ωΆ-Ώά-ώ]+)', r'\1[REDACTED_NAME]', text)
    text = re.sub(r'(στον ασθενή\s+)([Α-Ωα-ωΆ-Ώά-ώ]+)', r'\1[REDACTED_NAME]', text)
    
    return text

def write_secure_log(log_entry: str, log_file="data/execution_log.txt"):
    redacted_entry = redact_patient_info(log_entry)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(redacted_entry + "\n")

if __name__ == "__main__":
    sample = "Δώσε το αντιβιοτικό στον ασθενή Γεωργίου. ΑΜΚΑ: 12345678901."
    print("Original:", sample)
    print("Redacted:", redact_patient_info(sample))
