import ast
import numpy as np
import pandas as pd
from gensim.models import Word2Vec


# -----------------------------------------
# File paths
# -----------------------------------------

DATA_PATH = r"data/processed/processed_clauses.csv"
MODEL_PATH = r"models/legal_word2vec.model"
VECTOR_PATH = r"models/clause_vectors.npy"


# -----------------------------------------
# Load processed dataset
# -----------------------------------------

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully.")

print("\nDataset columns:")
print(df.columns.tolist())


# -----------------------------------------
# Convert tokens from string to Python list
# -----------------------------------------

df["tokens"] = df["tokens"].apply(ast.literal_eval)


# -----------------------------------------
# Load Word2Vec model
# -----------------------------------------

model = Word2Vec.load(MODEL_PATH)

print("\nWord2Vec model loaded successfully.")

print("Vector size:", model.vector_size)


# -----------------------------------------
# Function to create clause vector
# -----------------------------------------

def get_clause_vector(tokens):

    vectors = []

    for word in tokens:

        if word in model.wv:
            vectors.append(model.wv[word])

    # If no words are present in Word2Vec vocabulary
    if len(vectors) == 0:

        return np.zeros(model.vector_size)

    # Average all word vectors
    return np.mean(vectors, axis=0)


# -----------------------------------------
# Create vectors for all clauses
# -----------------------------------------

clause_vectors = np.array(
    [
        get_clause_vector(tokens)
        for tokens in df["tokens"]
    ]
)


# -----------------------------------------
# Save clause vectors
# -----------------------------------------

np.save(VECTOR_PATH, clause_vectors)


# -----------------------------------------
# Display information
# -----------------------------------------

print("\nClause vectors created successfully.")

print("Number of clauses:", len(clause_vectors))

print("Vector shape:", clause_vectors.shape)

print(
    f"\nClause vectors saved to: {VECTOR_PATH}"
)