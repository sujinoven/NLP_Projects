# Lifecycle stage 7 — Model Testing
import joblib
from src.data.preprocess import clean_text
 
model = joblib.load(
    "models/sentiment_model.pkl"
)
 
vectorizer = joblib.load(
    "models/tfidf_vectorizer.pkl"
)
 
while True:
 
    review = input(
        "\nEnter Review: "
    )
 
    X = vectorizer.transform(
        [clean_text(review)]
    )
 
    prediction = model.predict(X)
 
    print(
        "\nPrediction:",
        prediction[0]
    )