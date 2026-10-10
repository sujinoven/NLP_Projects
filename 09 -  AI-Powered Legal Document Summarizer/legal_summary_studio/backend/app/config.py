"""Environment settings. Paths in .env are relative to backend/."""
import os


class Config:
    MODEL_NAME = os.getenv("MODEL_NAME", "facebook/bart-large-cnn")
    DEVICE = os.getenv("DEVICE", "auto")
    LOCAL_FILES_ONLY = os.getenv("LOCAL_FILES_ONLY", "false").lower() == "true"
    MAX_CONTENT_LENGTH = 512 * 1024
    MAX_DOCUMENT_CHARS = int(os.getenv("MAX_DOCUMENT_CHARS", "60000"))
    MAX_DOCUMENT_TOKENS = int(os.getenv("MAX_DOCUMENT_TOKENS", "20000"))
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
