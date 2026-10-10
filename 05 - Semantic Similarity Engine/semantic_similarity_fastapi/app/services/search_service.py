from __future__ import annotations

import json
from threading import Lock

import joblib
import numpy as np
import pandas as pd
from gensim.models import FastText, Word2Vec
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

from app.config import (
    DOCUMENTS_PATH,
    FASTTEXT_MODEL_PATH,
    FASTTEXT_VECTORS_PATH,
    MODEL_METADATA_PATH,
    TFIDF_MATRIX_PATH,
    TFIDF_VECTORIZER_PATH,
    WORD2VEC_MODEL_PATH,
    WORD2VEC_VECTORS_PATH,
)
from app.services.preprocessing import preprocess_query


class ModelArtifactsMissingError(RuntimeError):
    pass


class SearchService:
    def __init__(self) -> None:
        self._lock = Lock()
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        with self._lock:
            if self._loaded:
                return

            required = [
                DOCUMENTS_PATH,
                TFIDF_VECTORIZER_PATH,
                TFIDF_MATRIX_PATH,
                WORD2VEC_MODEL_PATH,
                WORD2VEC_VECTORS_PATH,
                FASTTEXT_MODEL_PATH,
                FASTTEXT_VECTORS_PATH,
            ]

            missing = [str(path.name) for path in required if not path.exists()]
            if missing:
                raise ModelArtifactsMissingError(
                    "Model artifacts are missing: "
                    + ", ".join(missing)
                    + ". Run `python scripts/train_models.py` first."
                )

            self.documents: pd.DataFrame = joblib.load(DOCUMENTS_PATH)

            self.tfidf_vectorizer = joblib.load(TFIDF_VECTORIZER_PATH)
            self.tfidf_matrix = load_npz(TFIDF_MATRIX_PATH)

            self.word2vec_model = Word2Vec.load(str(WORD2VEC_MODEL_PATH))
            self.word2vec_vectors = np.load(
                WORD2VEC_VECTORS_PATH,
                mmap_mode="r",
            )

            self.fasttext_model = FastText.load(str(FASTTEXT_MODEL_PATH))
            self.fasttext_vectors = np.load(
                FASTTEXT_VECTORS_PATH,
                mmap_mode="r",
            )

            self.metadata = {}
            if MODEL_METADATA_PATH.exists():
                self.metadata = json.loads(
                    MODEL_METADATA_PATH.read_text(encoding="utf-8")
                )

            self._loaded = True

    @property
    def is_ready(self) -> bool:
        try:
            self._ensure_loaded()
            return True
        except ModelArtifactsMissingError:
            return False

    def _word2vec_query_vector(self, tokens: list[str]) -> np.ndarray:
        valid_words = [
            word for word in tokens if word in self.word2vec_model.wv
        ]

        if not valid_words:
            return np.zeros(self.word2vec_model.vector_size, dtype=np.float32)

        vectors = [self.word2vec_model.wv[word] for word in valid_words]
        return np.mean(vectors, axis=0)

    def _fasttext_query_vector(self, tokens: list[str]) -> np.ndarray:
        if not tokens:
            return np.zeros(self.fasttext_model.vector_size, dtype=np.float32)

        # Gensim FastText can construct vectors for OOV words
        # using character subword information.
        vectors = [self.fasttext_model.wv[word] for word in tokens]
        return np.mean(vectors, axis=0)

    def _format_results(
        self,
        indices: np.ndarray,
        scores: np.ndarray,
    ) -> list[dict]:
        rows = self.documents.iloc[indices][
            ["document_id", "category", "title", "content"]
        ].copy()

        output: list[dict] = []

        for rank, (_, row) in enumerate(rows.iterrows(), start=1):
            score = float(scores[indices[rank - 1]])
            output.append(
                {
                    "rank": rank,
                    "document_id": str(row["document_id"]),
                    "category": str(row["category"]),
                    "title": str(row["title"]),
                    "content": str(row["content"]),
                    "similarity_score": round(score, 6),
                }
            )

        return output

    def search(self, query: str, model: str, top_k: int = 5) -> dict:
        self._ensure_loaded()

        _, tokens, processed_query = preprocess_query(query)

        if not tokens:
            return {
                "query": query,
                "model": model,
                "top_k": top_k,
                "results": [],
                "message": "The query became empty after preprocessing.",
            }

        top_k = min(top_k, len(self.documents))

        if model == "tfidf":
            query_vector = self.tfidf_vectorizer.transform([processed_query])
            scores = cosine_similarity(
                query_vector,
                self.tfidf_matrix,
            ).flatten()

        elif model == "word2vec":
            query_vector = self._word2vec_query_vector(tokens)

            if np.allclose(query_vector, 0):
                return {
                    "query": query,
                    "model": model,
                    "top_k": top_k,
                    "results": [],
                    "message": "No known Word2Vec terms were found in the query.",
                }

            scores = cosine_similarity(
                query_vector.reshape(1, -1),
                self.word2vec_vectors,
            ).flatten()

        elif model == "fasttext":
            query_vector = self._fasttext_query_vector(tokens)

            if np.allclose(query_vector, 0):
                return {
                    "query": query,
                    "model": model,
                    "top_k": top_k,
                    "results": [],
                    "message": "No usable FastText terms were found in the query.",
                }

            scores = cosine_similarity(
                query_vector.reshape(1, -1),
                self.fasttext_vectors,
            ).flatten()

        else:
            raise ValueError(f"Unsupported model: {model}")

        top_indices = scores.argsort()[::-1][:top_k]

        return {
            "query": query,
            "model": model,
            "top_k": top_k,
            "results": self._format_results(top_indices, scores),
        }

    def compare(self, query: str, top_k: int = 5) -> dict:
        return {
            model: self.search(query, model, top_k)
            for model in ("tfidf", "word2vec", "fasttext")
        }


search_service = SearchService()
