import os
import json
import uuid
from datetime import datetime

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "feedback_history.json")

def _init_storage():
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    if not os.path.exists(STORAGE_FILE):
        # Add initial sample dataset items if empty
        initial_records = [
            {
                "id": str(uuid.uuid4()),
                "customer_name": "Sarah Jenkins",
                "category": "Electronics",
                "rating": 1,
                "text": "The battery died within 2 hours of unboxing and support hasn't responded. Very disappointed!",
                "sentiment": "negative",
                "confidence": 0.942,
                "telegram_alert_sent": True,
                "timestamp": "2026-08-29 09:30:15"
            },
            {
                "id": str(uuid.uuid4()),
                "customer_name": "Michael Chang",
                "category": "Home & Kitchen",
                "rating": 5,
                "text": "Absolutely amazing quality! Exceeded my expectations in design and build.",
                "sentiment": "positive",
                "confidence": 0.985,
                "telegram_alert_sent": False,
                "timestamp": "2026-08-29 09:45:00"
            },
            {
                "id": str(uuid.uuid4()),
                "customer_name": "Elena Rostova",
                "category": "Books",
                "rating": 3,
                "text": "The delivery arrived on time. Content is okay, nothing special but decent.",
                "sentiment": "neutral",
                "confidence": 0.721,
                "telegram_alert_sent": False,
                "timestamp": "2026-08-29 10:00:22"
            }
        ]
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_records, f, indent=2)

def get_all_feedback():
    _init_storage()
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def add_feedback_record(record: dict):
    records = get_all_feedback()
    if "id" not in record:
        record["id"] = str(uuid.uuid4())
    if "timestamp" not in record:
        record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    records.insert(0, record)  # Newest first
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    return record

def update_alert_status(record_id: str, status: bool):
    records = get_all_feedback()
    for rec in records:
        if rec.get("id") == record_id:
            rec["telegram_alert_sent"] = status
            break
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def clear_all_feedback():
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return True

def get_stats():
    records = get_all_feedback()
    total = len(records)
    if total == 0:
        return {
            "total": 0,
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "positive_pct": 0,
            "neutral_pct": 0,
            "negative_pct": 0,
            "alerts_sent": 0
        }
    
    positive = sum(1 for r in records if r.get("sentiment") == "positive")
    neutral = sum(1 for r in records if r.get("sentiment") == "neutral")
    negative = sum(1 for r in records if r.get("sentiment") == "negative")
    alerts = sum(1 for r in records if r.get("telegram_alert_sent"))

    return {
        "total": total,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "positive_pct": round((positive / total) * 100, 1),
        "neutral_pct": round((neutral / total) * 100, 1),
        "negative_pct": round((negative / total) * 100, 1),
        "alerts_sent": alerts
    }
