# Next Word Studio

A local full-stack application for Oven's next-word prediction project. A browser frontend calls a Python JSON API, which runs the saved TensorFlow GRU. No Node.js installation or cloud account is needed.

## Quick start in VS Code (Windows)

Prerequisite: 64-bit Python 3.11. Extract this ZIP and open the **next-word-app** folder in VS Code. Open Terminal > New Terminal and run these commands one at a time:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe import_bundle.py "C:\Users\sujin\Downloads\next_word_gru_bundle.zip"
.\.venv\Scripts\python.exe app.py
```

Change the bundle path if your Colab download is elsewhere. Open **http://127.0.0.1:8000** in your browser. No environment activation is required. The first prediction loads TensorFlow and the model and can take longer. Stop with Ctrl+C. On future visits only run the final command.

The trained weights are NOT included in the application ZIP: they were not available in the project workspace. Use your own `next_word_gru_bundle.zip` from the previous Colab step. Importing copies `best_gru.keras`, `tokenizer.json`, and `config.json` into `models/`. It does not execute the Python file in the bundle. The app's cleaner reproduces the cleaner supplied in this project; if you changed the Colab cleaner, update preprocessing.py to match before comparing results.

## Use it

Enter a phrase, select 1–50 new words, and click Generate continuation. The app displays the continuation, the top five suggestions for the original phrase, and a per-step probability table. Try “the company reported”, “the team won the”, or “the price of oil”. Input uses the latest 20 words (or the length in your config), with zeros added on the right. Generation chooses the highest-probability known word at each step. Padding and unknown tokens are excluded without renormalising probabilities.

The app uses GRU, selected on validation loss. Your reported test results were: RNN 19.91% accuracy / 157.83 perplexity, LSTM 17.30% / 206.11, GRU 20.05% / 149.78. These are recorded experiment results, not live measurements. 5.04% of test targets were unknown-token placeholders. Generated news text is not fact verification.

## Files explained

- `app.py`: serves the page and `/api/status`, `/api/generate` endpoints on localhost.
- `engine.py`: loads your tokenizer/model, prepares inputs, and predicts words.
- `preprocessing.py`: text cleaning shared with the training workflow.
- `static/`: HTML interface, CSS styling, JavaScript API requests.
- `import_bundle.py`: imports the three model data files from your ZIP.
- `models/`: your local model files, excluded from Git by default.

## Troubleshooting

- **Unrecognised quantization_config: None:** the app automatically retries loading a temporary archive with only this empty metadata removed. Original model files and weights remain unchanged. Actual quantization settings are never removed.

- **py not recognised:** install Python 3.11 from python.org with the Python launcher, then reopen VS Code.
- **Model setup needed:** import the Colab ZIP and refresh. If replacing a loaded model, restart the server.
- **Model loading/version error:** inspect `models/config.json` for `tensorflow_version`. Install that version with `.\.venv\Scripts\python.exe -m pip install "tensorflow==VERSION"`, replacing VERSION with the recorded value. The default requirements allow a recent compatible version; exact compatibility with your unseen bundle cannot be guaranteed.
- **DLL load failed on Windows:** TensorFlow may need the Microsoft Visual C++ Redistributable. See https://www.tensorflow.org/install/pip#windows-native.
- **Port in use:** run `app.py --port 8001`, then visit http://127.0.0.1:8001.
- **No GPU:** CPU inference works; GPU setup is unnecessary for testing this app.
- **Repeated/weak text:** greedy decoding and the five-epoch model can repeat or produce awkward language. This is model behaviour, not an app failure.

Use only your own trusted model bundle. This server is intended for local testing, bound to 127.0.0.1, not public hosting.

## Verification

Run `python -m unittest discover -s tests -v` for API validation, preprocessing and bundle-import checks. These use a clearly isolated test double for inference; they do not certify model quality. Real model inference must be checked after importing your Colab bundle.
