# Lifecycle stage 5 — Model Building (TF-IDF features)
import pandas as pd
import joblib
 
from sklearn.feature_extraction.text import (TfidfVectorizer)
 
df = pd.read_csv("data/processed/cleaned_reviews.csv")
df["clean_review"] = df["clean_review"].fillna("")
vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1,2))
 
X = vectorizer.fit_transform( df["clean_review"])
 
joblib.dump( vectorizer,"models/tfidf_vectorizer.pkl")
 
print(X.shape)