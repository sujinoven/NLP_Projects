# Legal Summary Studio

A modular **Flutter frontend + Flask REST API** for English legal-document summarization using **facebook/bart-large-cnn**. Paste a document, choose a summary-length target, generate a copyable summary, inspect pattern-based fact matches, and optionally compare it with a human reference using ROUGE precision, recall and F1.

The default frontend target is **Flutter Web in Chrome on Windows**. This is real Dart/Flutter source, not an HTML imitation. Native Android/iOS/Windows runner projects are not included. Model weights, Python/Flutter SDKs and virtual environments are not included in the ZIP.

## 1. Extract the ZIP

In PowerShell, navigate to the folder containing the downloaded ZIP:

```powershell
Expand-Archive -LiteralPath .\Legal-Summary-Studio-Flutter-Flask.zip -DestinationPath .\Legal-Summary-Studio
cd .\Legal-Summary-Studio\legal_summary_studio
```

Or use **Extract All**, then open the `legal_summary_studio` folder in VS Code. Run the following commands from the stated folders.

## 2. Prerequisites

- Python **3.11 or 3.12**, with pip and the Windows `py` launcher.
- Flutter stable 3.35 or newer with Dart 3.9 or newer, on PATH; Chrome for the default run target.
- Internet for package installation and the first model download. Reserve several GB for dependencies, model cache and Flutter tools. BART-large is memory intensive; 16 GB system RAM is a practical starting point. CPU works but generation can take minutes; a compatible CUDA PyTorch installation can accelerate it.

Check your installations:

```powershell
py --version
flutter --version
flutter doctor
flutter devices
```

Install Flutter using https://docs.flutter.dev/install and web setup guidance at https://docs.flutter.dev/platform-integration/web/setup. If a command is not found, install that SDK and restart your terminal after updating PATH.

## 3. Set up the backend

From the project root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
Copy-Item .env.example .env
```

Use `py -3.11` instead if that is your installed supported version. Explicit Python paths avoid PowerShell activation-policy problems. Do not overwrite an existing `.env` if you have customized it.

Download/load the real checkpoint and run one real inference:

```powershell
.\.venv\Scripts\python.exe download_model.py
```

The first run downloads the tokenizer and model from Hugging Face. Later runs reuse the cache. The script prints a genuine model summary and a fact-match report; inspect the facts manually. It does not claim the summary is legally correct.

Start the API in **Terminal 1**, from `backend`:

```powershell
.\.venv\Scripts\python.exe run.py
```

Leave this terminal open. The default API is `http://127.0.0.1:5001`. The server uses Waitress with one process and a nonblocking inference lock, so a concurrent generation receives HTTP 429 instead of loading another model. Health requests remain available. No debug reloader is used.

## 4. Start Flutter

Open **Terminal 2** at the project root:

```powershell
cd frontend
flutter pub get
flutter run -d chrome --web-port=5173 --dart-define=API_BASE_URL=http://127.0.0.1:5001
```

If Chrome is not detected:

```powershell
flutter run -d web-server --web-hostname=127.0.0.1 --web-port=5173 --dart-define=API_BASE_URL=http://127.0.0.1:5001
```

Then visit `http://127.0.0.1:5173` in your browser. Both origins `http://localhost:5173` and `http://127.0.0.1:5173` are allowed by the API. The compiled API address is set by `--dart-define`; changing it requires restarting/rebuilding Flutter.

After initial setup, optional launchers are available at `scripts/start-backend.ps1` and `scripts/start-frontend.ps1`. The direct commands above work without changing PowerShell script execution policy.

## 5. Use the application

1. Check the API badge. `not_loaded` means the server is reachable but BART has not been loaded in that server process yet.
2. Paste English plain text, or select **Try a sample**.
3. Choose a target ratio (10–60%) and maximum output tokens (120/220/320/400).
4. Optionally expand **Evaluate with ROUGE** and supply a separate human reference summary.
5. Select **Summarize document**. The first server request loads the model into RAM even if files were already downloaded.
6. Copy the result and inspect amounts, dates, parties, conditions, negations and omissions against the original.

There is no PDF/DOCX upload or OCR in this version: paste already-extracted text, matching the assessment's plain-text input requirement. Documents are processed in memory; this application does not intentionally save source text or summaries. The inference runs locally, with no hosted generation API. Hugging Face is used to obtain model files; normal package/model download metadata still involves network requests.

## 6. Test the API

With Terminal 1 running, open another PowerShell terminal in `backend`:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/api/health
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5001/api/summarize -ContentType 'application/json' -InFile .\sample_request.json
```

The second command is **real inference**, not a canned response. It can take time on CPU.

## 7. Automated checks

Backend checks, from `backend`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe -m pytest -q
```

These check validation, API errors, CORS, token coverage, cleanup, fact matching, known ROUGE values and map/reduce control flow. Most model orchestration tests use a test double. An optional integration test runs real PyTorch/Transformers generation with a tiny randomly initialized BART model; it skips if those dependencies are absent. None of these tests download the pretrained checkpoint or establish summary quality.

Flutter checks, from `frontend`:

```powershell
dart format lib test
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=http://127.0.0.1:5001
```

After both services start, manually verify: empty input validation; sample generation; copy button; ROUGE hidden without a reference; precision/recall/F1 with a reference; long input processing; offline API message; and narrow-window layout. See `docs/VALIDATION.md` for what was actually verified during packaging.

## 8. Folder structure

```text
legal_summary_studio/
  README.md
  backend/
    app/
      __init__.py                 Flask factory and JSON error handling
      config.py                   Environment settings and limits
      routes.py                   API endpoints and request validation
      services/
        summarizer.py             Lazy BART loading and map/reduce inference
        text_processing.py        Cleanup and lossless token-ID windows
        facts.py                  Pattern-based match and omission report
        metrics.py                ROUGE precision, recall and F1
    tests/                        API and service tests
    .env.example
    requirements.txt
    requirements-lock.txt          Resolved inference dependency versions
    requirements-test.txt
    pytest.ini
    run.py                        Waitress entry point
    download_model.py             Real-model download/inference check
    sample_request.json
  frontend/
    lib/
      main.dart                   Flutter entry point
      app.dart                    Theme and application shell
      config/api_config.dart      API address
      models/summary_result.dart  Typed response model
      services/api_service.dart   HTTP requests, timeout and errors
      screens/summarizer_screen.dart
      widgets/section_card.dart
      widgets/result_panel.dart
    test/                         HTTP contract and result-widget tests
    web/                          Flutter browser bootstrap
    pubspec.yaml
    analysis_options.yaml
  scripts/                        Optional PowerShell launchers
  docs/
    API.md
    ARCHITECTURE.md
    VALIDATION.md
```

## 9. Configuration and troubleshooting

Edit `backend/.env` and restart the API:

| Variable | Default | Meaning |
|---|---|---|
| `PORT` | `5001` | API port |
| `HOST` | `127.0.0.1` | Local machine only |
| `DEVICE` | `auto` | `auto`, `cpu`, or `cuda` |
| `HF_HOME` | `.model_cache` in example | Model cache, relative to backend |
| `LOCAL_FILES_ONLY` | `false` | Set `true` after a complete download for offline model loading |
| `MAX_DOCUMENT_CHARS` | `60000` | HTTP document character cap |
| `MAX_DOCUMENT_TOKENS` | `20000` | Actual BART content-token cap |
| `CORS_ORIGINS` | localhost/127.0.0.1 port 5173 | Allowed browser origins |

- **Port blocked / WinError 10013:** try `PORT=5002` and restart Flutter with `--dart-define=API_BASE_URL=http://127.0.0.1:5002`.
- **Model cannot load:** run `download_model.py` for the full exception, check internet and free disk/RAM. If CUDA fails, set `DEVICE=cpu`. PyTorch installation guidance: https://pytorch.org/get-started/locally/.
- **Offline startup:** the cache must contain both tokenizer and safetensors weights. Download first, then set `LOCAL_FILES_ONLY=true`.
- **HTTP 429:** another request is active; wait for it to finish. A frontend timeout does not cancel backend inference. There is no task queue in this local prototype.
- **HTTP 413:** reduce document length. Character checks run before model loading; token limits require the tokenizer.
- **Wrong API address/CORS:** use the matching port and add the exact frontend origin to `.env`. CORS is not authentication.
- **Slow CPU inference:** start with a short document and 120 output tokens. Four-beam BART-large generation is computationally expensive.
- **Page stays on the startup message:** allow 30–60 seconds on the first debug launch, keep the Flutter terminal open, and inspect its errors. After changing web bootstrap files, stop Flutter with Ctrl+C, rerun the frontend command, then refresh the browser with Ctrl+F5. A backend/model download does not block the initial frontend screen.
- **Dependency reproducibility:** `requirements-lock.txt` records the inference package versions used for the Windows/Python 3.12 integration check. `requirements.txt` keeps the broader intended ranges for deliberate upgrades. Flutter's generated `pubspec.lock` is included. Full pretrained-checkpoint generation still needs the separate download/inference check.

This package is a local coursework/portfolio prototype, not an authenticated public service or a guarantee of legal accuracy. It has no additional legal fine-tuning. Fact matching and ROUGE are diagnostics, not a factual correctness certificate.
