import pandas as pd
from src.data.load_data import load_data
from src.data.preprocess import clean_batch

def process_dataset():

    print("Script Started")

    df = load_data("data/raw")

    print("Dataset Loaded")

    combined = df["news_headline"].astype(str)+" "+df["news_article"].astype(str)

    texts=combined.str.lower()
    texts=texts.str.replace(r"https\S+","",regex=True)
    texts = texts.str.replace(r"[^a-zA-Z ]","",regex=True)

    df["clean_text"] =clean_batch(texts)

    print("Cleaning Completed")

    df.to_csv("data/processed/cleaned_news.csv",index=False)

    print("File Saved")