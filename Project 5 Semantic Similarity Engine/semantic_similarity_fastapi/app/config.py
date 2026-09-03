from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
TEMPLATE_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

DATASET_PATH = DATA_DIR / "knowledge_base.csv"

APP_NAME = os.getenv("APP_NAME", "Semantic Similarity Search System")

TFIDF_VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
TFIDF_MATRIX_PATH = MODEL_DIR / "tfidf_matrix.npz"
WORD2VEC_MODEL_PATH = MODEL_DIR / "word2vec.model"
WORD2VEC_VECTORS_PATH = MODEL_DIR / "word2vec_vectors.npy"
FASTTEXT_MODEL_PATH = MODEL_DIR / "fasttext.model"
FASTTEXT_VECTORS_PATH = MODEL_DIR / "fasttext_vectors.npy"
DOCUMENTS_PATH = MODEL_DIR / "documents.pkl"
MODEL_METADATA_PATH = MODEL_DIR / "model_metadata.json"
