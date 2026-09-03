from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from gensim.models import FastText, Word2Vec
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import (  # noqa: E402
    DATASET_PATH,
    DOCUMENTS_PATH,
    FASTTEXT_MODEL_PATH,
    FASTTEXT_VECTORS_PATH,
    MODEL_DIR,
    MODEL_METADATA_PATH,
    TFIDF_MATRIX_PATH,
    TFIDF_VECTORIZER_PATH,
    WORD2VEC_MODEL_PATH,
    WORD2VEC_VECTORS_PATH,
)
from app.services.preprocessing import clean_text, tokenize_text  # noqa: E402


REQUIRED_COLUMNS = {
    "document_id",
    "category",
    "title",
    "content",
    "keywords",
}


def validate_dataset(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(sorted(missing))
        )


def build_search_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["search_text"] = (
        df["title"].fillna("").astype(str)
        + " "
        + df["content"].fillna("").astype(str)
        + " "
        + df["keywords"].fillna("").astype(str)
    )

    df["clean_text"] = df["search_text"].apply(clean_text)
    df["tokens"] = df["clean_text"].apply(tokenize_text)
    df["processed_text"] = df["tokens"].apply(" ".join)

    return df


def average_word2vec(tokens: list[str], model: Word2Vec) -> np.ndarray:
    valid = [word for word in tokens if word in model.wv]

    if not valid:
        return np.zeros(model.vector_size, dtype=np.float32)

    return np.mean([model.wv[word] for word in valid], axis=0)


def average_fasttext(tokens: list[str], model: FastText) -> np.ndarray:
    if not tokens:
        return np.zeros(model.vector_size, dtype=np.float32)

    return np.mean([model.wv[word] for word in tokens], axis=0)


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_PATH}. "
            "Copy knowledge_base.csv into the data/ folder."
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    validate_dataset(df)

    print(f"Rows: {len(df):,}")
    print("Building searchable text...")
    df = build_search_columns(df)

    empty_count = int((df["processed_text"].str.len() == 0).sum())
    print(f"Empty processed documents: {empty_count}")

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------
    print("\nTraining TF-IDF...")
    tfidf_vectorizer = TfidfVectorizer(max_features=20000)
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["processed_text"])

    joblib.dump(tfidf_vectorizer, TFIDF_VECTORIZER_PATH)
    save_npz(TFIDF_MATRIX_PATH, tfidf_matrix)

    print(
        f"TF-IDF shape: {tfidf_matrix.shape}, "
        f"vocabulary: {len(tfidf_vectorizer.vocabulary_):,}"
    )

    # --------------------------------------------------------
    # Word2Vec
    # --------------------------------------------------------
    print("\nTraining Word2Vec...")
    word2vec_model = Word2Vec(
        sentences=df["tokens"],
        vector_size=100,
        window=5,
        min_count=2,
        workers=4,
        sg=1,
        epochs=10,
    )
    word2vec_model.save(str(WORD2VEC_MODEL_PATH))

    print("Creating Word2Vec document vectors...")
    word2vec_vectors = np.vstack(
        df["tokens"].apply(
            lambda tokens: average_word2vec(tokens, word2vec_model)
        )
    ).astype(np.float32)

    np.save(WORD2VEC_VECTORS_PATH, word2vec_vectors)

    # --------------------------------------------------------
    # FastText
    # --------------------------------------------------------
    print("\nTraining FastText...")
    fasttext_model = FastText(
        sentences=df["tokens"],
        vector_size=100,
        window=5,
        min_count=2,
        workers=4,
        sg=1,
        epochs=10,
        min_n=3,
        max_n=6,
    )
    fasttext_model.save(str(FASTTEXT_MODEL_PATH))

    print("Creating FastText document vectors...")
    fasttext_vectors = np.vstack(
        df["tokens"].apply(
            lambda tokens: average_fasttext(tokens, fasttext_model)
        )
    ).astype(np.float32)

    np.save(FASTTEXT_VECTORS_PATH, fasttext_vectors)

    # Save only columns required during serving.
    documents = df[
        ["document_id", "category", "title", "content"]
    ].copy()
    joblib.dump(documents, DOCUMENTS_PATH)

    metadata = {
        "document_count": int(len(df)),
        "categories": sorted(df["category"].astype(str).unique().tolist()),
        "tfidf_vocabulary_size": int(len(tfidf_vectorizer.vocabulary_)),
        "tfidf_shape": list(tfidf_matrix.shape),
        "word2vec_vocabulary_size": int(len(word2vec_model.wv)),
        "word2vec_vector_size": int(word2vec_model.vector_size),
        "fasttext_vocabulary_size": int(len(fasttext_model.wv)),
        "fasttext_vector_size": int(fasttext_model.vector_size),
    }

    MODEL_METADATA_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print("\nTraining complete.")
    print(f"Artifacts saved to: {MODEL_DIR}")


if __name__ == "__main__":
    main()
