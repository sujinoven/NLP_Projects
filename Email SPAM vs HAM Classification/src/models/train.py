import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from src.models.build_model import build_model 

df = pd.read_csv("data/processed/cleaned_emails.csv")
df["clean_email"] = df["clean_email"].fillna("")

vectorizer = joblib.load("models/count_vectorizer.pkl")

X =vectorizer.transform(df["clean_email"])
y=df["label"]

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)

model = build_model()

model.fit(X_train,y_train)

joblib.dump(model,"models/spam_model.pkl")

print("Training Completed")