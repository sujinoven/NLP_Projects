import nltk
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("wordnet")

import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

#Important Legal words whcih we should not remove. But,might have a greater meaning in Legal

LEGAL_IMPORTANT_WORDS={"shall","must","may","not","no","without","unless","except","required"}

#Get Standard English Stopwords
STOP_WORDS = set(stopwords.words("english"))

#Keeping legally important words

STOP_WORDS =STOP_WORDS-LEGAL_IMPORTANT_WORDS

#Create Lemmatizer

Lemmatizer = WordNetLemmatizer()

def clean_text(text):
    """
    Clean and Tokenize Legal clause.
    """

    #COnvert to lower case
    text = str(text).lower()

    #remove Punctuation and Numbers
    text =re.sub(r"[^a-zA-Z\s]"," ",text)

    #Tokenize
    tokens = word_tokenize(text)

    #Remove Stopwords
    tokens=[word for word in tokens if word not in STOP_WORDS]

    #Lemmatize
    tokens = [Lemmatizer.lemmatize(word) for word in tokens]

    return tokens

def prepare_Dataset(df):
    """
    Prepare Legal Clause Dataset.
    """

    #Makign a copy.So,the original dataframe is not modified

    df =df.copy()

    #Dropping columns that doesn't require for our NLP Model
 

    df = df.drop(columns=["Unnamed: 0","totalwords","totalletters"],
                 errors="ignore")

    #Remove rows where clause_text is missing

    df=df.dropna(subset=["clause_text"])

    #Making sure that the clause_text is string
    df["clause_text"]=df["clause_text"].astype(str)

    #Remove Duplicate Clauses
    df=df.drop_duplicates(subset=["clause_text"])

    #Create tokenized/cleaned text
    df["tokens"] = df["clause_text"].apply(clean_text)

    #Remove clauses that became empty after preprocessing
    df=df[df["tokens"].map(len)>0]

    #Reset Row Numbers
    df=df.reset_index(drop=True)

    return df

def main():

    #Location of the Original csv
    input_path="data/raw/legal_docs.csv"
   
    #Location where processed data will be saved
    output_path="data/processed/processed_clauses.csv"

    #Load Dataset
    df=pd.read_csv(input_path)

    print("Original Dataset shape:")
    print(df.shape)

    #Prepare Datset
    df=prepare_Dataset(df)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nProcessed Dataset Shape:")
    print(df.shape)

    print("\nProcessed Columns:")
    print(df.columns.tolist())

    print("\nFirst 5 Processed Rows:")
    print(df.head())

    #Save Processed Dataset

    df.to_csv(output_path,index=False)

    print(f"\nProcessed Dataset saved to:{output_path}")

if __name__=="__main__":
    main()