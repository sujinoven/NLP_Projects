"""
Legal Clause Similarity Engine - FastAPI Backend
=================================================

This module implements the FastAPI backend for the Legal Clause Similarity Engine.
It loads pre-trained Word2Vec models, pre-computed clause vectors, and the processed
legal clause dataset to provide semantic search functionality.

Beginner Explanation:
---------------------
1. FastAPI: A fast web framework for building APIs with Python.
2. Word2Vec: Converts words into 100-dimensional numerical vectors where similar words have similar vectors.
3. Clause Vector: Calculated by taking the average vector of all known words in a legal clause.
4. Cosine Similarity: Measures the angle between the query vector and dataset vectors (score from -1 to 1).
"""

import ast
from pathlib import Path
import re
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

import nltk
from gensim.models import Word2Vec
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ============================================================
# NLTK RESOURCE DOWNLOADS
# Ensure required NLTK tokenizers and wordlists are available
# ============================================================
for resource in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

# ============================================================
# RELATIVE FILE PATH DEFINITIONS
# Locate dataset and models relative to project root
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "processed_clauses.csv"
MODEL_PATH = BASE_DIR / "models" / "legal_word2vec.model"
VECTOR_PATH = BASE_DIR / "models" / "clause_vectors.npy"

# ============================================================
# NLP CONSTANTS & PREPROCESSING SETUP
# Important legal words preserved during stopword removal
# ============================================================
LEGAL_IMPORTANT_WORDS = {
    "shall",
    "must",
    "may",
    "not",
    "no",
    "without",
    "unless",
    "except",
    "required"
}

# Standard English stopwords excluding legal terms
try:
    ENGLISH_STOPWORDS = set(stopwords.words("english"))
except Exception:
    ENGLISH_STOPWORDS = set()

STOP_WORDS = ENGLISH_STOPWORDS - LEGAL_IMPORTANT_WORDS
LEMMATIZER = WordNetLemmatizer()

# ============================================================
# GLOBAL DATA & MODEL HOLDERS
# Models are loaded once at startup for high performance
# ============================================================
df_clauses: Optional[pd.DataFrame] = None
w2v_model: Optional[Word2Vec] = None
clause_vectors: Optional[np.ndarray] = None


def load_artifacts():
    """
    Load dataset, Word2Vec model, and clause vectors on startup.
    This avoids expensive disk reads on every user search request.
    """
    global df_clauses, w2v_model, clause_vectors

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Processed dataset not found at {DATA_PATH}")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Word2Vec model not found at {MODEL_PATH}")

    if not VECTOR_PATH.exists():
        raise FileNotFoundError(f"Clause vectors file not found at {VECTOR_PATH}")

    # 1. Load Processed Dataset
    df_clauses = pd.read_csv(DATA_PATH)
    
    # Ensure tokens column is safely evaluated to Python lists if needed
    if "tokens" in df_clauses.columns:
        def parse_tokens(tok_val):
            if isinstance(tok_val, str):
                try:
                    return ast.literal_eval(tok_val)
                except Exception:
                    return tok_val.split()
            return tok_val
        df_clauses["tokens"] = df_clauses["tokens"].apply(parse_tokens)

    # 2. Load Word2Vec Model
    w2v_model = Word2Vec.load(str(MODEL_PATH))

    # 3. Load Pre-computed Clause Vectors
    clause_vectors = np.load(str(VECTOR_PATH))

    print("==================================================")
    print("Legal Clause Similarity Engine initialized!")
    print(f"Total Legal Clauses Loaded : {len(df_clauses)}")
    print(f"Word2Vec Vector Dimension  : {w2v_model.vector_size}")
    print(f"Clause Matrix Shape        : {clause_vectors.shape}")
    print("==================================================")


# Initialize global artifacts immediately upon file import
load_artifacts()


# ============================================================
# PREPROCESSING & HELPER FUNCTIONS
# ============================================================

def clean_text(text: str) -> List[str]:
    """
    Clean and tokenize input legal clause.
    
    Steps:
    1. Lowercase text
    2. Strip non-alphabetic characters & numbers
    3. Tokenize words
    4. Remove general English stopwords (preserving legal terms)
    5. Lemmatize words to base form
    """
    # Step 1: Lowercase
    text_lower = str(text).lower()

    # Step 2: Remove punctuation and numbers
    text_clean = re.sub(r"[^a-zA-Z\s]", " ", text_lower)

    # Step 3: Tokenize into individual words
    tokens = word_tokenize(text_clean)

    # Step 4: Filter out stopwords while preserving important legal terms
    filtered_tokens = [word for word in tokens if word not in STOP_WORDS]

    # Step 5: Lemmatize words (e.g. "paying" -> "pay")
    lemmatized_tokens = [LEMMATIZER.lemmatize(word) for word in filtered_tokens]

    return lemmatized_tokens


def get_clause_vector(tokens: List[str]) -> np.ndarray:
    """
    Calculate the average 100-dimensional vector representation for a query.
    If no words are found in the Word2Vec vocabulary, returns a zero vector.
    """
    vectors = []
    for word in tokens:
        if word in w2v_model.wv:
            vectors.append(w2v_model.wv[word])

    if len(vectors) == 0:
        return np.zeros(w2v_model.vector_size)

    return np.mean(vectors, axis=0)


def cosine_similarity(query_vector: np.ndarray, dataset_vectors: np.ndarray) -> np.ndarray:
    """
    Calculate Cosine Similarity between query vector and all dataset clause vectors.
    
    Formula:
        Cosine Similarity = (Query · Vector_i) / (||Query|| * ||Vector_i||)
    """
    query_norm = np.linalg.norm(query_vector)
    dataset_norms = np.linalg.norm(dataset_vectors, axis=1)

    # Compute dot product between query and all stored vectors
    dot_product = np.dot(dataset_vectors, query_vector)

    # Prevent division by zero
    denominator = query_norm * dataset_norms
    denominator[denominator == 0] = 1e-10

    similarities = dot_product / denominator
    return similarities


# ============================================================
# FASTAPI APP & MIDDLEWARE SETUP
# ============================================================

app = FastAPI(
    title="Legal Clause Similarity Engine API",
    description="Semantic search engine for legal clauses using pre-trained Word2Vec.",
    version="1.0.0"
)

# CORS Middleware setup for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PYDANTIC INPUT MODEL FOR API SEARCH
# ============================================================

class SearchRequest(BaseModel):
    clause: str = Field(
        ...,
        description="The legal clause text to find similarities for.",
        json_schema_extra={"example": "The tenant shall pay monthly rent before the fifth day of each month."}
    )
    top_k: Optional[int] = Field(
        5,
        ge=1,
        le=20,
        description="Number of top similar clauses to retrieve (1 to 20)."
    )

    @field_validator("clause")

    @classmethod
    def clause_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Clause text cannot be empty.")
        return value


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", summary="Root Endpoint")
def read_root():
    """
    Return basic status message confirming API is operational.
    """
    return {
        "message": "Legal Clause Similarity Engine API is running."
    }


@app.get("/health", summary="Health Check Endpoint")
def check_health():
    """
    Return dataset clause count and vector dimension size dynamically.
    """
    return {
        "status": "healthy",
        "clauses": len(df_clauses),
        "vector_size": w2v_model.vector_size
    }


@app.post("/search", summary="Search Similar Legal Clauses")
def search_similar_clauses(request: SearchRequest):
    """
    Main Endpoint: Accepts a legal clause and retrieves top_k semantically similar clauses.
    """
    query_text = request.clause.strip()

    if not query_text:
        return {
            "error": "Please enter a valid legal clause."
        }

    # Step 1: Preprocess user query
    tokens = clean_text(query_text)

    # Step 2: Create query vector
    query_vec = get_clause_vector(tokens)

    # Step 3: Check if query vector is zero (meaning no words in Word2Vec vocabulary)
    if np.all(query_vec == 0):
        return {
            "error": "None of the words in your clause were found in the model vocabulary. Please try another legal clause."
        }

    # Step 4: Calculate cosine similarity against all stored clause vectors
    similarities = cosine_similarity(query_vec, clause_vectors)

    # Step 5: Validate and bound top_k parameter
    top_k = request.top_k if request.top_k is not None else 5
    top_k = max(1, min(top_k, len(df_clauses)))

    # Step 6: Get indices of top_k highest similarity scores (descending order)
    top_indices = np.argsort(similarities)[::-1][:top_k]

    # Step 7: Construct list of matching clause results
    results = []
    for rank, idx in enumerate(top_indices, start=1):
        row = df_clauses.iloc[idx]
        score = float(similarities[idx])
        
        # Standardize score between 0 and 1 for display if slightly negative or > 1
        score = float(np.clip(score, -1.0, 1.0))
        
        results.append({
            "rank": rank,
            "clause_text": str(row["clause_text"]),
            "clause_type": str(row.get("clause_type", "General")),
            "similarity_score": round(score, 4)
        })

    # Step 8: Return structured search JSON
    return {
        "query": query_text,
        "processed_tokens": tokens,
        "results": results
    }