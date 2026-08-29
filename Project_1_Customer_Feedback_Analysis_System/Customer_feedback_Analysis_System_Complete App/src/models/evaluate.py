# Lifecycle stage 8 — Model Evaluation
import pandas as pd
import joblib
 
from sklearn.metrics import (
    classification_report,
    confusion_matrix
)
 
from sklearn.model_selection import (
    train_test_split
)
 
df = pd.read_csv(
    "data/processed/cleaned_reviews.csv"
)
 
model = joblib.load(
    "models/sentiment_model.pkl"
)

df["clean_review"] = df["clean_review"].fillna("")
vectorizer = joblib.load(
    "models/tfidf_vectorizer.pkl"
)
 
X = vectorizer.transform(
    df["clean_review"]
)
 
y = df["sentiment"]
 
_, X_test, _, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
)
 
predictions = model.predict(X_test)
 
print(
    classification_report(
        y_test,
        predictions
    )
)
 
# Fix the label order so the grid is readable and the
# negative class always sits in the top-left corner.
labels = ["negative", "neutral", "positive"]
 
cm = confusion_matrix(
    y_test,
    predictions,
    labels=labels
)
 
cm_table = pd.DataFrame(
    cm,
    index=["actual_negative", "actual_neutral", "actual_positive"],
    columns=["pred_negative", "pred_neutral", "pred_positive"]
)
 
print("\nConfusion Matrix (rows = actual, columns = predicted)")
print(cm_table)