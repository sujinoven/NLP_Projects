import pandas as pd
from src.data.preprocess import clean_batch

def process_dataset():

    print("Script Started")

    df = pd.read_csv("data/raw/email_spam_dataset.csv")

    print("Dataset Loadded")

    #Lowercasing and Regex are fast as vectorized pandas ops,so we do them here and leave only tokenizing/lemmatizing to spaCy.

    texts = df["message"].astype(str).str.lower()
    texts = texts.str.replace(r"http:\S+", "",regex=True)
    texts = texts.str.replace(r"[^a-zA-Z ]", "", regex=True)

    df["clean_email"] = clean_batch(texts)

    print("Clenaing Completed")

    df.to_csv("data/processed/cleaned_emails.csv",index=False)

    print("File Saved.")