import re
from functools import lru_cache

import nltk
from nltk.corpus import stopwords


@lru_cache(maxsize=1)
def get_stop_words() -> set[str]:
    try:
        words = set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        words = set(stopwords.words("english"))

    # Preserve negation because it can reverse user intent.
    words -= {"no", "not", "nor"}
    return words


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_text(text: str) -> list[str]:
    stop_words = get_stop_words()
    return [token for token in text.split() if token not in stop_words]


def preprocess_query(text: str) -> tuple[str, list[str], str]:
    cleaned = clean_text(text)
    tokens = tokenize_text(cleaned)
    processed = " ".join(tokens)
    return cleaned, tokens, processed
