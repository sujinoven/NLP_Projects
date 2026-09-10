"""HTTP input validation stays separate from inference."""
import math
from flask import Blueprint, current_app, jsonify, request
from .services.summarizer import ServiceError

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/health")
def health():
    return jsonify(current_app.extensions["summarizer"].health())


@api.post("/summarize")
def summarize():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object with a text field."), 400
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        return jsonify(error="text must be a non-empty string."), 400
    if len(text) > current_app.config["MAX_DOCUMENT_CHARS"]:
        return jsonify(error="Document exceeds the character limit."), 413
    ratio = data.get("target_ratio", 0.3)
    if isinstance(ratio, bool) or not isinstance(ratio, (int, float)) or not math.isfinite(ratio) or not 0.1 <= ratio <= 0.6:
        return jsonify(error="target_ratio must be between 0.1 and 0.6."), 400
    limit = data.get("max_summary_tokens", 220)
    if type(limit) is not int or not 32 <= limit <= 400:
        return jsonify(error="max_summary_tokens must be an integer from 32 to 400."), 400
    reference = data.get("reference")
    if reference is not None and (not isinstance(reference, str) or len(reference) > 20000):
        return jsonify(error="reference must be a string of at most 20000 characters."), 400
    try:
        result = current_app.extensions["summarizer"].summarize(
            text, ratio, limit, reference.strip() if reference else None
        )
        return jsonify(result)
    except ServiceError as exc:
        return jsonify(error=str(exc)), exc.status
