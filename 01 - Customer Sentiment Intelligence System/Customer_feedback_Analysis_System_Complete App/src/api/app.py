# Lifecycle stage 9 — Model Deployment (hand-off) & Phase 13 Telegram Alerts
import os
import sys
import numpy as np
import joblib
import nltk
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from nltk.sentiment import SentimentIntensityAnalyzer

# Add project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.data.preprocess import clean_text
from src.alerts.telegram_alert import (
    send_negative_alert, 
    send_test_alert, 
    auto_detect_chat_id, 
    get_config, 
    save_config
)
from src.utils.storage import (
    add_feedback_record, 
    get_all_feedback, 
    get_stats, 
    clear_all_feedback,
    update_alert_status
)

app = FastAPI(
    title="Customer Feedback Sentiment Analyzer & Telegram Alert API",
    description="Production REST API for real-time customer feedback sentiment analysis and automated Telegram alerting.",
    version="1.0.0"
)

# Download VADER lexicon if missing
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

vader_analyzer = SentimentIntensityAnalyzer()

# Load trained ML Model & TF-IDF Vectorizer
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "sentiment_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "tfidf_vectorizer.pkl")

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("Successfully loaded sentiment model and TF-IDF vectorizer!")
except Exception as e:
    print(f"Error loading model files: {e}")
    model = None
    vectorizer = None

# Request & Response Schemas
class ReviewRequest(BaseModel):
    text: str
    customer_name: Optional[str] = "Anonymous Customer"
    category: Optional[str] = "General Feedback"
    rating: Optional[int] = None

class BatchReviewRequest(BaseModel):
    reviews: List[ReviewRequest]

class TelegramConfigRequest(BaseModel):
    token: str
    chat_id: str

@app.post("/predict")
def predict(review: ReviewRequest):
    """
    Core prediction endpoint. Cleans review text, runs TF-IDF vectorizer + Logistic Regression + VADER,
    calculates sentiment label & confidence, and triggers Telegram alert if negative.
    """
    if not model or not vectorizer:
        raise HTTPException(status_code=500, detail="ML Model or Vectorizer is not loaded")

    if not review.text or not review.text.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty")

    cleaned = clean_text(review.text)
    X = vectorizer.transform([cleaned])

    # ML Model prediction
    ml_sentiment = str(model.predict(X)[0])
    
    # ML Confidence score
    confidence = 0.85
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[0]
        confidence = float(np.max(probs))

    # VADER sentiment scoring (Phase 5 rule)
    vader_scores = vader_analyzer.polarity_scores(review.text)
    vader_compound = vader_scores["compound"]

    # Hybrid High-Recall Decision Logic (Prioritizes surfacing negative feedback for business owner)
    if vader_compound <= -0.05 or ml_sentiment == "negative" or (review.rating and review.rating <= 2):
        sentiment = "negative"
        confidence = max(confidence, abs(vader_compound))
    elif vader_compound >= 0.05 and ml_sentiment == "positive":
        sentiment = "positive"
        confidence = max(confidence, vader_compound)
    elif vader_compound >= 0.4:
        sentiment = "positive"
        confidence = max(confidence, vader_compound)
    else:
        sentiment = "neutral"
        confidence = round(1.0 - abs(vader_compound), 4)

    alert_sent = False
    alert_error = None

    # Push to Telegram if review is negative
    if sentiment == "negative":
        try:
            send_negative_alert(
                review=review.text,
                sentiment=sentiment,
                confidence=confidence,
                customer_name=review.customer_name,
                category=review.category,
                rating=review.rating
            )
            alert_sent = True
        except Exception as err:
            alert_error = str(err)
            print(f"Failed to send Telegram alert: {err}")

    # Store record
    record = add_feedback_record({
        "customer_name": review.customer_name or "Anonymous Customer",
        "category": review.category or "General Feedback",
        "rating": review.rating,
        "text": review.text,
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "telegram_alert_sent": alert_sent,
        "alert_error": alert_error
    })

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "telegram_alert_sent": alert_sent,
        "alert_error": alert_error,
        "record_id": record.get("id")
    }

@app.post("/api/batch-predict")
def batch_predict(batch: BatchReviewRequest):
    results = []
    for item in batch.reviews:
        try:
            res = predict(item)
            results.append(res)
        except Exception as e:
            results.append({"text": item.text, "error": str(e)})
    return {"processed": len(results), "results": results}

@app.get("/api/history")
def history(sentiment: Optional[str] = None):
    records = get_all_feedback()
    if sentiment:
        records = [r for r in records if r.get("sentiment") == sentiment.lower()]
    return {"records": records, "total": len(records)}

@app.delete("/api/history")
def clear_history():
    clear_all_feedback()
    return {"message": "All feedback history cleared"}

@app.post("/api/history/{record_id}/resend-alert")
def resend_alert(record_id: str):
    records = get_all_feedback()
    target = next((r for r in records if r.get("id") == record_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Record not found")
    
    try:
        send_negative_alert(
            review=target.get("text"),
            sentiment=target.get("sentiment", "negative"),
            confidence=target.get("confidence"),
            customer_name=target.get("customer_name"),
            category=target.get("category"),
            rating=target.get("rating")
        )
        update_alert_status(record_id, True)
        return {"success": True, "message": "Alert re-sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
def stats():
    return get_stats()

# Telegram Integration Endpoints
@app.get("/api/telegram/config")
def telegram_config():
    token, chat_id = get_config()
    masked_token = f"{token[:8]}...{token[-5:]}" if len(token) > 15 else token
    return {
        "token": token,
        "masked_token": masked_token,
        "chat_id": chat_id,
        "is_configured": bool(token and chat_id)
    }

@app.post("/api/telegram/config")
def update_telegram_config(config: TelegramConfigRequest):
    save_config(config.token, config.chat_id)
    return {"success": True, "message": "Telegram configuration saved"}

@app.post("/api/telegram/test")
def trigger_test_alert(chat_id: Optional[str] = None):
    try:
        res = send_test_alert(override_chat_id=chat_id)
        return {"success": True, "message": "Test message sent to Telegram!", "response": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test alert: {str(e)}")

@app.post("/api/telegram/auto-detect")
def auto_detect_telegram():
    res = auto_detect_chat_id()
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

# Static Web Application Serving
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))