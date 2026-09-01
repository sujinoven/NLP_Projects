import pandas as pd
import joblib

from sklearn.metrics import classification_report,confusion_matrix
from sklearn.model_selection import train_test_split

model = joblib.load("models/spam_model.pkl")

vectorizer = joblib.load("models/count_vectorizer.pkl")

# Load processed dataset
df = pd.read_csv("data/processed/cleaned_emails.csv")
df["clean_email"] = df["clean_email"].fillna("")

X=vectorizer.transform(df["clean_email"])
y=df["label"]

_,X_test,_,y_test = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)

predictions = model.predict(X_test)

print(classification_report(y_test,predictions))

#Fixing the label order. So, the grid is readable and the spam class always sits in the left corner

labels=["spam","ham"]

cm = confusion_matrix(y_test,predictions,labels=labels)

cm_table = pd.DataFrame(cm,index=["actual_spam","actual_ham"],columns=["pred_spam","pred_ham"])

print("\nConfusion Matrix (rows=actual,column=predicted)")

print(cm_table)