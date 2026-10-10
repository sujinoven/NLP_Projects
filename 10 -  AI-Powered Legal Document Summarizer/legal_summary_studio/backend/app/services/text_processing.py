"""Conservative cleanup: keep case, numbers and paragraph boundaries."""
import re


def preprocess(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    # Only remove standalone page labels; preserve 'See Page 3 of 12'.
    lines = [line for line in text.splitlines()
             if not re.fullmatch(r"\s*Page\s+\d+(?:\s+of\s+\d+)?\s*", line, re.I)]
    text = "\n".join(re.sub(r"[^\S\n]+", " ", line).strip() for line in lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def token_windows(ids, capacity=1022, overlap=64):
    """Lossless token-ID windows, including oversized sentences.

    Special tokens are added AFTER splitting. No decode/re-encode cycle can
    alter the input IDs. Token overlap is deliberate (not sentence overlap).
    """
    if capacity < 1 or not 0 <= overlap < capacity:
        raise ValueError("Invalid chunk capacity or overlap")
    if not ids:
        return []
    windows = []
    start = 0
    while start < len(ids):
        end = min(start + capacity, len(ids))
        windows.append(ids[start:end])
        if end == len(ids):
            break
        start = end - overlap
    return windows
