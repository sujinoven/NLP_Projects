# DistilBERT Extractive Question Answering AI System

A lightweight, beginner-friendly web application for extractive Question Answering (QA) powered by fine-tuned **DistilBERT** (trained on SQuAD v1), **FastAPI**, **PyTorch**, **Hugging Face Transformers**, and a modern **Vanilla HTML/CSS/JS** single-page frontend.

---

## 📁 Project Architecture & Folder Structure

```
question-answering-app/
├── app/
│   ├── main.py          # FastAPI application routes & static file mounting
│   ├── schemas.py       # Pydantic request/response models & input validation
│   ├── qa_service.py    # DistilBERT model loading, token windowing & span scoring
│   └── static/
│       ├── index.html   # Semantic UI layout & SQuAD v1 notice
│       ├── styles.css   # Modern light theme & typography styling
│       └── app.js       # Dynamic event handlers & span highlighting
├── model/               # Extracted local model directory (config.json, model.safetensors, etc.)
├── tests/
│   ├── test_schemas.py  # Unit tests for input validation
│   ├── test_qa_service.py # Unit tests for token sliding window & span selection
│   └── test_api.py      # Integration tests for FastAPI endpoints
├── requirements.txt     # Python dependencies
├── .gitignore          # Git exclusion rules (model weights, virtual environments)
└── README.md            # Application documentation & setup guide
```

---

## ⚡ Key Features

- **Extractive QA Inference**: Answers questions directly from user-provided context passages.
- **Overlapping Sliding Token Windows**: Handles long passages with `max_length=384`, `stride=128`, and `truncation="only_second"`.
- **Character Offset Mapping**: Maps model output tokens back to exact character start/end positions in original text.
- **Combined Span Scoring**: Evaluates candidate spans across sliding windows by summing start and end logit values ($start\_logit + end\_logit$).
- **Single-Command Serving**: Served completely through FastAPI — no Node.js build step required.
- **Modern UI**: Clean light-themed user interface with sample context presets, character counters, loading states, error handling, and visual text highlighting (`<mark>`).

---

## 🚀 Quickstart Guide (Windows PowerShell)

Follow these steps in **Windows PowerShell** to extract the model, set up the virtual environment, install dependencies, and launch the application.

### Step 1: Open PowerShell and Navigate to the Workspace Directory

```powershell
cd "d:\ProITBridge\Courses\NLP_Course\Project 13 Question Answering AI System"
```

### Step 2: Extract the Fine-Tuned Model Weights

Extract `distilbert_squad_model.zip` into `question-answering-app/model/`:

```powershell
Expand-Archive -Path "distilbert_squad_model.zip" -DestinationPath "question-answering-app/model_temp" -Force
Get-ChildItem -Path "question-answering-app/model_temp/*" | Move-Item -Destination "question-answering-app/model/" -Force
Remove-Item -Path "question-answering-app/model_temp" -Recurse -Force
```

*Note: Verify that `question-answering-app/model/` contains `config.json`, `model.safetensors`, `tokenizer.json`, and `tokenizer_config.json`.*

### Step 3: Create and Activate Python Virtual Environment

```powershell
cd "question-answering-app"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Run the Web Application

Launch the server with Uvicorn:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Running Automated Tests

The repository includes pytest suites covering schema validation, token windowing logic, and FastAPI endpoints.

```powershell
# Run all tests
pytest tests/ -v
```

### Real Model Verification

To verify inference with the real local model weights:

```powershell
python -c "from app.qa_service import QAService; from pathlib import Path; s = QAService(Path('model')); s.load_model(); print(s.answer_question('DistilBERT is a small, fast model created by Hugging Face.', 'Who created DistilBERT?'))"
```

---

## ⚠️ Model Limitations (SQuAD v1 Notice)

This model was fine-tuned on the **SQuAD v1.1** dataset. SQuAD v1 consists exclusively of context passages where an answer is guaranteed to exist.

- **No Unanswerable Question Detection**: The model evaluates candidate spans from the context passage and selects the span with the highest logit score, even if the question is unrelated or unanswerable.
- **Do Not Rely on Raw Logit Scores as Percentages**: Logit values reflect relative token preferences, not normalized probabilities or confidence percentages.
