import pandas as pd

DATA_PATH = r"D:\ProITBridge\Courses\NLP_Course\Project 4 Legal Clause Similarity Engine\data\raw\legal_docs.csv"

df = pd.read_csv(DATA_PATH)

print(df.head())
print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nData types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicated Rows:")
print(df.duplicated().sum())

print("\nClause Types:")
print(df["clause_type"].value_counts())