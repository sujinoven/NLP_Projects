# Language Studio

A local Streamlit app for Oven's Transformer translation project. Translate support messages between English, French, Spanish, Hindi and Tamil with NLLB-200 distilled 600M.

## What is included

- Source-language detection or a manual source selector for short messages.
- Automatic detection and exact protection of likely product names, error codes, technical identifiers, versions, links and email addresses. No prefilled brand or manual term list is needed.
- Per-occurrence placeholder validation, including repeated names.
- Optional sentence-by-sentence translation to compare omissions and context.
- Text and JSON downloads, clear errors, and no automatic message logging.
- CPU support, automatic CUDA selection when your PyTorch installation supports it.
- Real inference only: no mock translations in the app.

## Windows setup

Install Python 3.11 or 3.12 from https://www.python.org/downloads/ if needed. A Python version installed inside another application is not necessarily on your PATH.

If you received the ZIP, extract it first. Open PowerShell or the VS Code terminal **in the extracted Language-Studio folder**. Do not run the app from inside the ZIP.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If you installed Python 3.11, replace `py -3.12` with `py -3.11`. No virtual-environment activation or PowerShell execution-policy change is required.

Open **http://127.0.0.1:8501** in your browser. Stop the server with Ctrl+C. Subsequent launches need only the last command. `start.ps1` is an optional shortcut after installation.

If port 8501 is occupied:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

Then open http://127.0.0.1:8502.

### First model download

The model loads when the first actual translation is requested, not when the page opens. First use needs internet and downloads several gigabytes of model assets. Cached assets are reused. Allow several gigabytes of free disk space and RAM; 8 GB RAM may be tight and 16 GB gives more room. CPU translation can take substantially longer than your Colab T4.

Model assets are cached in `.cache/huggingface/hub` inside this project, including after a restart. Set `TRANSLATION_CACHE` to another folder if desired. If a connection interrupts the download, retry; Hugging Face can reuse partial cached downloads.

No Hugging Face token is normally required for this public model. Your input messages are processed on this computer; Hugging Face receives model-download requests, not your message text from this app. The server binds to localhost by default. Do not expose it publicly without authentication, resource controls and a licensing review.

The dependency range intentionally uses Transformers 4.x for this standalone app. It does not require you to change your Colab environment. The checkpoint is the same; floating-point precision and library differences may change outputs.

### NVIDIA GPU (optional)

CPU works by default. If you want GPU acceleration, install the PyTorch build appropriate to your computer using the official selector at https://pytorch.org/get-started/locally/. Your computer does not automatically inherit the Colab T4. The app chooses CUDA only if `torch.cuda.is_available()` is true.

### Use a saved NLLB checkpoint later

The app currently uses the pretrained model; it has not been fine-tuned. For a future **full compatible NLLB model and tokenizer folder**:

```powershell
$env:TRANSLATION_MODEL = 'C:\path\to\saved-nllb-model'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Restart the app after changing this. A LoRA adapter alone is not a full checkpoint and is not supported by this loader. Do not include downloaded weights in the app ZIP.

## Try it

1. Select English as source and French as target.
2. Enter `Please help me reset my password.` and click **Translate message**.
3. Translate `My CloudDesk account shows error E403. Please help!` to Hindi. The automatic protection preview should identify CloudDesk and E403 without manual entry.
4. Try `E403` by itself: the app preserves it without loading a model.
5. Try `Help!` with automatic detection: it asks for a manual source rather than guessing.
6. Try a mixed Hindi/English message: it reports the current limitation instead of claiming success.

Only a translation matching the current inputs is shown. Input edits hide stale results, and a failed request clears the prior result.

## Tests

Logic checks with test doubles (no model download; these do not establish translation quality):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Actual model inference (downloads weights if needed):

```powershell
.\.venv\Scripts\python.exe smoke_test.py
```

See VALIDATION.md for what was actually run during app creation. A successful inference check is not a formal translation benchmark.

## How the files fit together

- `app.py`: interface, session state and downloadable results.
- `engine.py`: source detection, term protection, model loading and generation.
- `protection.py`: automatic candidate detection using technical formats, name spelling and product context, without a brand-name dictionary.
- `tests/`: tests of validation and interface behaviour.
- `smoke_test.py`: real checkpoint inference check.
- `.streamlit/config.toml`: local server and visual theme.

The model is cached and reused. A lock serialises generation and changes to `tokenizer.src_lang` because the model resource is shared across sessions.

## Known boundaries

- Detection scores are not calibrated accuracy. Romanised Hindi/Tamil and short or ambiguous text can fail.
- The mixed-script check is conservative. It may reject loanwords and does not detect mixtures that share a script, such as English/French. Same-language returns are explicitly labelled unchanged.
- Protection is automatic and rule-based, not a universal named-entity recogniser. Camel-case names, title-case names in product/account context, quoted product labels, codes, versions, acronyms, URLs and email addresses are recognised. Lowercase or ambiguous names without context can be missed; acronyms can be false positives. No brand names are built into the detector. Ordinary account/password terminology is translated rather than universally frozen.
- Detected terms are case-sensitive whole terms. They are not matched inside larger words. Exact marker counts do not prove correct placement or good grammar. Marker failure releases no translation. The UI previews detected items before translation and lists restored items afterward.
- Simple sentence splitting can mishandle abbreviations and lose context. Use the toggle to compare.
- Inputs are capped at 4,000 characters and 512 tokens per translated segment. Outputs must end naturally within 256 new tokens; incomplete outputs are rejected.
- Unknown generated tokens are rejected rather than silently hidden.
- The model can still omit content or produce awkward grammar. Review meaning, tone, urgency and technical details.
- This app does not complete fine-tuning, the planned multilingual benchmark, mixed-language support, or the mandatory assessment video.

## Model and license

NLLB-200 distilled 600M is licensed CC-BY-NC-4.0 and is intended for research, not released for production deployment. This package is an educational prototype, not a commercial support product. Model card: https://huggingface.co/facebook/nllb-200-distilled-600M

The app uses Streamlit, PyTorch, Hugging Face Transformers, SentencePiece and langdetect. Their respective licenses apply. No evaluation dataset or pretrained weights are redistributed in this ZIP.
