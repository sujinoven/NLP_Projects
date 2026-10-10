from pathlib import Path
import re

import numpy as np
import pandas as pd


class FastTextRecommender:
    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir
        self.products: pd.DataFrame | None = None
        self.vectors: np.ndarray | None = None
        self.model = None
        self.error: str | None = None
        self.load()

    @property
    def ready(self) -> bool:
        return self.products is not None and self.vectors is not None

    def load(self) -> None:
        products_path = self.artifacts_dir / "prepared_products.csv"
        vectors_path = self.artifacts_dir / "fasttext_product_vectors.npy"
        model_path = self.artifacts_dir / "fasttext.model"

        missing = [path.name for path in (products_path, vectors_path) if not path.exists()]
        if missing:
            self.error = "Missing artifact files: " + ", ".join(missing)
            return

        try:
            products = pd.read_csv(products_path)
            vectors = np.load(vectors_path, allow_pickle=False).astype("float32")

            if len(products) != len(vectors):
                raise ValueError("Product rows and vector rows do not match")

            lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
            self.vectors = vectors / np.maximum(lengths, 1e-12)
            self.products = products.reset_index(drop=True)

            if model_path.exists():
                from gensim.models import FastText
                self.model = FastText.load(str(model_path))

            self.error = None
        except Exception as exc:
            self.error = f"Could not load recommendation artifacts: {exc}"

    def search_products(self, query: str, limit: int = 8) -> list[dict]:
        self._ensure_ready()
        matches = self.products[
            self.products["name"].astype(str).str.contains(query, case=False, regex=False, na=False)
        ].head(limit)
        return [self._product_record(index) for index in matches.index]

    def recommend(self, query: str, limit: int = 8) -> tuple[dict, list[dict]]:
        self._ensure_ready()
        query_vector = self._query_vector(query)

        if query_vector is None:
            matches = self.products[
                self.products["name"].astype(str).str.contains(query, case=False, regex=False, na=False)
            ]
            if matches.empty:
                raise LookupError("No matching product was found")
            selected_index = int(matches.index[0])
            query_vector = self.vectors[selected_index]
        else:
            selected_index = int(np.argmax(self.vectors @ query_vector))

        scores = self.vectors @ query_vector
        scores[selected_index] = -1
        top_indices = np.argsort(scores)[::-1][:limit]

        selected = self._product_record(selected_index)
        recommendations = [
            self._product_record(int(index), float(scores[index])) for index in top_indices
        ]
        return selected, recommendations

    def _query_vector(self, query: str) -> np.ndarray | None:
        if self.model is None:
            return None
        words = re.sub(r"[^a-z\s]", " ", query.lower()).split()
        if not words:
            return None
        vector = np.mean([self.model.wv[word] for word in words], axis=0).astype("float32")
        length = np.linalg.norm(vector)
        return vector / length if length else None

    def _product_record(self, index: int, score: float | None = None) -> dict:
        row = self.products.iloc[index]

        def clean(column: str):
            value = row.get(column)
            return None if pd.isna(value) else value

        return {
            "id": index,
            "name": str(clean("name") or "Unknown product"),
            "main_category": str(clean("main_category") or "Unknown"),
            "sub_category": str(clean("sub_category") or "Unknown"),
            "image": clean("image"),
            "link": clean("link"),
            "ratings": clean("ratings"),
            "no_of_ratings": clean("no_of_ratings"),
            "discount_price": clean("discount_price"),
            "actual_price": clean("actual_price"),
            "similarity_score": score,
        }

    def _ensure_ready(self) -> None:
        if not self.ready:
            raise RuntimeError(self.error or "Recommendation service is not ready")
