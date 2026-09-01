import pandas as pd
df = pd.read_csv("data/processed/cleaned_news.csv")
print(df["news_category"].value_counts())