# Architecture and learning guide

## Data flow

```text
Flutter screen
  -> ApiService (JSON over HTTP)
  -> Flask routes (validate)
  -> Summarizer service
       -> conservative cleanup
       -> matching BART tokenizer
       -> bounded token-ID windows
       -> BART encoder/decoder + four-beam generation
       -> bounded repeated reduction for long documents
       -> pattern match report + optional reference ROUGE
  -> JSON response model
  -> Flutter result panel
```

The backend owns model inference and evaluation. The frontend owns user input, display and HTTP communication. A Flask application factory permits injecting a fake service in tests without downloading model weights.

## Changes from the explained notebook

- A fixed 40-token minimum is removed. Inputs below 24 content tokens return unchanged with a warning. This favors retaining tiny clauses but does not promise compression for them.
- Token-ID windows reserve room for special tokens and cover every content token, including very long sentences. A 64-token overlap provides local context. This deliberately replaces the notebook's sentence-based chunker: boundaries can split a sentence, but text is not silently truncated.
- Model inputs are assembled directly from those IDs with an explicit batch dimension. No decode/re-encode expansion or `truncation=True` hides overflow.
- Map/reduce has a progress check and a six-pass limit, so pathological reduction fails explicitly rather than recursing forever.
- Page labels are removed only when they occupy a standalone line. Inline page references and paragraph boundaries remain.
- Pattern matching supports one-letter party names, boundaries, amounts, selected dates, percentages and numeric durations. No matches gives null precision rather than a misleading perfect score. Role reversals and negation remain unresolved.
- Source items absent from the summary are shown for manual review. This is not a required-fact recall metric.
- ROUGE uses a user-provided reference and exposes precision, recall and F1. No fallback dataset is silently substituted.
- One model object is loaded lazily per server process. Inference is serialized; health is independently available.

## Suggested reading order

1. `backend/app/services/text_processing.py`
2. `backend/app/services/summarizer.py`
3. `backend/app/services/facts.py` and `metrics.py`
4. `backend/app/routes.py` and `app/__init__.py`
5. `frontend/lib/models/summary_result.dart`
6. `frontend/lib/services/api_service.dart`
7. `frontend/lib/screens/summarizer_screen.dart` and `widgets/result_panel.dart`

## Limits

BART's checkpoint was fine-tuned on news, not these legal documents. Repeated compression can omit obligations. A hard maximum can end a summary abruptly. Four-beam search and no-repeat trigrams do not guarantee faithfulness. Numeric dates, language coverage and named-entity patterns are incomplete. The UI is English/plain-text oriented; no training, corpus benchmark, OCR, authentication, persistence or multi-user queue is included.

## Official implementation references

- Flask application factories: https://flask.palletsprojects.com/en/stable/patterns/appfactories/
- Flask testing: https://flask.palletsprojects.com/en/stable/testing/
- Flutter web setup: https://docs.flutter.dev/platform-integration/web/setup
- BART architecture/configuration: https://huggingface.co/docs/transformers/model_doc/bart
- Hugging Face generation parameters: https://huggingface.co/docs/transformers/main_classes/text_generation
