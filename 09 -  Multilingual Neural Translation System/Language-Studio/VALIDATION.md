# Validation record

Built and checked on Windows with Python 3.12.

## Passed

- 20 automated tests: 16 translation-logic/protection tests and 4 Streamlit interface tests.
- Python syntax compilation.
- Dependency consistency (`pip check`).
- Live browser inspection of the localhost app: layout, inputs and language selectors render.
- A live E403-only request returned E403 as Preserved without requiring the model.
- Interface tests cover empty input, example loading, clear, download controls and hiding stale results.
- Automatic protection checks cover names not in a brand dictionary, product-name context in English/French/Spanish, labelled non-Latin names, error codes, versions, URLs, emails, repeated terms, and preserving the translatability of ordinary words. The UI has no manual term field or prefilled brand.

The interface tests use a test double for translation. They do not prove real model inference.

## Real-model check

The first real-model download was interrupted after about 809 MB of a roughly 2.46 GB weight file. A standard retry stalled and was stopped. A further attempt with the official Hugging Face Xet helper did not complete and was stopped. There is no confirmed real-model inference result on this computer. No model-download process was intentionally left running at handoff.

The app needs a complete cached model or a successful first-use download. The ZIP excludes weights, caches and the virtual environment. See README.md for the real-model smoke-test command.

## Quality boundaries

No fine-tuning or multilingual benchmark was performed during this app build. Existing Colab results are not presented as locally verified app results. Mixed-script translation is blocked, not solved. Term preservation and successful execution are not translation-quality guarantees.
