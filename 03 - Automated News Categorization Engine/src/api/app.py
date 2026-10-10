# Lifecycle stage 9 — Model Deployment (hand-off)
 
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from src.data.preprocess import clean_text
from src.routing.store import route_article
 
app = FastAPI()
 
model = joblib.load("models/new_model.pkl")
 
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
 
 
class Article(BaseModel):
    text: str
 
 
@app.post("/predict")
def predict(article: Article):
 
    X = vectorizer.transform([clean_text(article.text)])
 
    category = model.predict(X)[0]

 
    route_article(article.text, category)
 
    return {"category": category}