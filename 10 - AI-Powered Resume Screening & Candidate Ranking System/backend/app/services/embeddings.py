import numpy as np
import torch
from typing import Dict, List, Tuple
from app.config import settings

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class EmbeddingModelManager:
    _instance = None
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            if SentenceTransformer is None:
                raise ImportError("sentence-transformers is not installed.")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Loading embedding model '{settings.EMBEDDING_MODEL}' on device '{device}'...")
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL, device=device)
            print("Embedding model loaded successfully.")
        return cls._model

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None

def get_device_name() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"

def chunk_text(text: str, max_words: int = settings.MAX_CHUNK_WORDS) -> List[str]:
    """
    Group lines into chunks under a word budget.
    Never splits a line, so a bullet stays whole and can be quoted as evidence.
    """
    chunks, buffer, count = [], [], 0

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        n = len(line.split())

        if count + n > max_words and buffer:
            chunks.append(" ".join(buffer))
            buffer, count = [], 0

        buffer.append(line)
        count += n

    if buffer:
        chunks.append(" ".join(buffer))

    return chunks

def embed(texts: List[str], is_query: bool = False) -> np.ndarray:
    """
    Generate normalized embeddings for a list of text strings.
    If is_query=True, prepends the BGE query instruction prefix.
    """
    model = EmbeddingModelManager.get_model()
    dim = model.get_sentence_embedding_dimension()

    if not texts:
        return np.zeros((0, dim), dtype="float32")

    if is_query:
        texts = [settings.QUERY_PREFIX + t for t in texts]

    return model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    )

def embed_sections(sections: Dict[str, str], is_query: bool = False) -> Tuple[Dict[str, List[str]], Dict[str, np.ndarray]]:
    """
    Chunk and embed each section.
    Returns (chunks_dict, vecs_dict)
    """
    chunks = {s: chunk_text(t) for s, t in sections.items()}
    vecs = {s: embed(c, is_query=is_query) for s, c in chunks.items()}
    return chunks, vecs
