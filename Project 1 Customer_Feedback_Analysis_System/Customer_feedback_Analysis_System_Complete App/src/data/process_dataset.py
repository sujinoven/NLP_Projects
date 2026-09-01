# Lifecycle stage 4 — Data Preparation (full dataset)
import pandas as pd
 
from src.data.preprocess import create_sentiment, clean_batch
 
def process_dataset():
 
    print("Script Started")
 
    df = pd.read_csv("data/raw/Reviews.csv")
 
    print("Dataset Loaded")
 
    # Random sample, NOT head() — the file is grouped by product,
    # so the first rows are a narrow slice. random_state keeps it repeatable.
    df = df.sample(1500, random_state=42)
 
    df["sentiment"] = df["reviews.text"].apply(create_sentiment)
 
    print("Sentiment Created")
 
    # Lowercasing + regex are fast as vectorized pandas ops,
    # so we do them here and leave only tokenizing/lemmatizing to spaCy.
    texts = df["reviews.text"].astype(str).str.lower()
    texts = texts.str.replace(r"http\S+", "", regex=True)
    texts = texts.str.replace(r"[^a-zA-Z ]", "", regex=True)
 
    df["clean_review"] = clean_batch(texts)
 
    print("Cleaning Completed")
 
    df.to_csv(
 
        "data/processed/cleaned_reviews.csv",
 
        index=False
 
    )
 
    print("File Saved")