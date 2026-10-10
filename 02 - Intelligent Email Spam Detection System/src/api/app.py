from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from src.data.preprocess import clean_text
from src.quarantine.store import quarantine_email

app =FastAPI()

model = joblib.load("models/spam_model.pkl")
vectorizer = joblib.load("models/count_vectorizer.pkl")

class Email(BaseModel):
    text: str 

@app.post("/predict")
def predict(email: Email):
    X=vectorizer.transform([clean_text(email.text)])
    label = model.predict(X)[0]

    if label=="spam":
        qurantine_email(email.text,label)

    return {"label": label}