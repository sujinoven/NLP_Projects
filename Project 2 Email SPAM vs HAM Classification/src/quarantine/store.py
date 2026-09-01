import csv
import os
from datetime import datetime
 
QUARANTINE_FILE = "data/quarantine/quarantine.csv"
 
 
def quarantine_email(email_text, label):
 
    os.makedirs("data/quarantine", exist_ok=True)
 
    new_file = not os.path.exists(QUARANTINE_FILE)
 
    with open(QUARANTINE_FILE, "a", newline="", encoding="utf-8") as f:
 
        writer = csv.writer(f)
 
        if new_file:
            writer.writerow(["timestamp", "label", "email_text"])
 
        writer.writerow([datetime.now().isoformat(), label, email_text])