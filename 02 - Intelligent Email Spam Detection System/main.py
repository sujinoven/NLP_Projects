from src.data.load_data import load_data
df = load_data("data/raw/email_spam_dataset.csv")
print(df.head())
print(df.columns)
print(df["label"].value_counts())