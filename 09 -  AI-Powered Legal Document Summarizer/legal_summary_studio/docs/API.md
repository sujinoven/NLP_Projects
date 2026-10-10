# API contract

Base URL: `http://127.0.0.1:5001`

## GET /api/health

HTTP 200 means the Flask service is alive. It does not guarantee model readiness.

```json
{"status":"ok","model":"facebook/bart-large-cnn","model_state":"not_loaded","device":null,"busy":false}
```

Model states: `not_loaded`, `loading`, `ready`, `error`.

## POST /api/summarize

Content-Type: `application/json`.

| Field | Required | Validation |
|---|---|---|
| `text` | Yes | Nonblank string; maximum 60,000 characters by default |
| `target_ratio` | No | Finite number 0.1–0.6, default 0.3 |
| `max_summary_tokens` | No | Integer 32–400, default 220 |
| `reference` | No | Human reference summary, maximum 20,000 characters |

Response fields: `summary`, `model`, `input_tokens`, `summary_tokens`, `compression_ratio`, `target_ratio`, `chunks`, `passes`, `elapsed_seconds`, `facts`, `rouge`, `warnings`.

Token counts exclude special tokens. `compression_ratio` is output/input token count, not percentage reduction. Output length is a target, not guaranteed. Tiny inputs can be returned unchanged and are explicitly labeled.

`facts` contains `match_precision` (0–1 or null when nothing can be checked), `matched`, `not_found_in_source`, `source_items_not_in_summary`, and `note`. Missing items can be legitimate omissions; exact text matching does not establish entailment.

`rouge` is null without a reference. Otherwise `rouge1`, `rouge2` and `rougeL` each contain `precision`, `recall` and `f1`, all 0–1. Stemming is enabled. Scores describe the supplied reference pair, not corpus performance.

All error responses use `{"error":"Readable message"}`:

| Status | Meaning |
|---|---|
| 400 | Invalid JSON/fields or empty document after cleanup |
| 413 | Request, character or model-token limit exceeded |
| 422 | Empty model output or safe reduction limit reached |
| 429 | Inference already active |
| 500 | Unexpected processing failure |
| 503 | Model could not load |

There is no automatic retry of generation, to avoid duplicate expensive work. No source text is intentionally logged by application code.
