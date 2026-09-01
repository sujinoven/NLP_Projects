import pandas as pd
from gensim.models import Word2Vec

DATA_PATH = r"D:\ProITBridge\Courses\NLP_Course\Project 4 Legal Clause Similarity Engine\data\processed\processed_clauses.csv"
MODEL_PATH =r"models/legal_word2vec.model"

df=pd.read_csv(DATA_PATH)

sentences=df["tokens"].apply(eval).tolist()

model =Word2Vec(sentences=sentences,vector_size=100,window=5,min_count=2,workers=4,sg=1,epochs=20)

model.save(MODEL_PATH)

print("Word2Vec Model Trained Successfully.")
#Testing it

print(model.wv.most_similar("tenant", topn=10))