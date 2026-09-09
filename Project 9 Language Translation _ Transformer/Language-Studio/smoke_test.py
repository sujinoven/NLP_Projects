"""Explicit real-model check: downloads model weights if not cached."""
from engine import NllbBackend, translate_message

if __name__ == "__main__":
    backend = NllbBackend()
    result = translate_message(
        "Please help me reset my password.", "English", "French", [], True, backend
    )
    assert result.translation.strip()
    assert result.translation != result.original
    print("Device:", backend.device)
    print("Source:", result.original)
    print("Translation:", result.translation)
    print("Real-model inference completed. This is not a quality benchmark.")
