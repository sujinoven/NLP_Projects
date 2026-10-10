# Full-Stack AI Resume Screening System (NER & BGE Embeddings)

A full-stack Resume Screening application using HuggingFace BERT NER (`yashpwr/resume-ner-bert`) and BGE Large embeddings (`BAAI/bge-large-en-v1.5`) for automated candidate section matching, similarity ranking, contact extraction, and interactive evidence review.

---

## Technical Stack & Architecture

- **Backend**: Python FastAPI, PyMuPDF, python-docx, Sentence-Transformers (`BAAI/bge-large-en-v1.5`), HuggingFace Transformers (`yashpwr/resume-ner-bert`), Pytest.
- **Frontend**: React 18, Vite, Tailwind CSS, Glassmorphic UI design system, Lucide React icons, Axios.
- **Processing Pipeline**:
  - Text extraction from `.pdf`, `.docx`, and `.txt` files with OCR warning detection for empty/scanned PDFs.
  - Sentence-level regex cleaning and whitespace normalization.
  - Resume & Job Description section parsing (`summary`, `skills`, `experience`, `projects`, `education`, `required_skills`, `responsibilities`, etc.) with fallback to `full_text` when unstructured.
  - Word budget line chunking (max 60 words) preserving bullet boundary integrity.
  - Mean-of-max cosine dot-product matrix similarity scoring.
  - Relative fit score min-max scaling pool normalization (`0-100`).
  - Contact regex extraction (email, phone, LinkedIn, GitHub) and BERT NER candidate name profiling.

---

## Repository Layout

```
resume-screening/
├── frontend/                     # React + Vite UI
│   ├── src/
│   │   ├── components/           # JobDescriptionInput, ResumeUpload, ResultsTable, CandidateDetailModal, Header, etc.
│   │   ├── services/             # api.js (Axios API client)
│   │   ├── App.jsx               # Main React Dashboard
│   │   └── index.css             # Glassmorphism & custom design system
│   ├── package.json
│   ├── .env.example
│   └── vite.config.js
├── backend/                      # Python FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # /health and /screen endpoints
│   │   ├── services/
│   │   │   ├── extraction.py     # Document text extraction + OCR warning
│   │   │   ├── preprocessing.py  # Text cleaning & regex normalization
│   │   │   ├── sections.py       # Resume & JD section splitting
│   │   │   ├── embeddings.py     # BGE model singleton & chunk embedding
│   │   │   ├── scoring.py        # Mean-of-max comparison & fit score scaling
│   │   │   └── entities.py       # BERT NER & contact extraction
│   │   ├── schemas.py            # Pydantic response models
│   │   ├── config.py             # App configuration settings
│   │   └── main.py               # FastAPI entrypoint
│   ├── tests/                    # Unit tests suite (11 passed tests)
│   ├── requirements.txt          # Python backend dependencies
│   └── .env.example
├── notebooks/                    # Preserved original Jupyter Notebook
│   └── Resume Screening Script.ipynb
├── .gitignore                    # Local caches, uploads, node_modules exclusions
└── README.md                     # Setup, usage, and verification guide
```

---

## Setup & Running Instructions (Windows PowerShell)

### 1. Backend Setup & Startup

Open PowerShell in the project root directory:

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Configure environment file
Copy-Item backend\.env.example backend\.env

# Set PYTHONPATH and start FastAPI server
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

> [!NOTE]
> **First-Run Model Download & CPU Performance Expectation**:
> On the first backend startup or screening request, HuggingFace models (`BAAI/bge-large-en-v1.5` ~1.3GB and `yashpwr/resume-ner-bert` ~400MB) will download automatically into local cache. Model loading on CPU takes ~10–30 seconds. On subsequent requests, models remain loaded in memory for fast inference.

---

### 2. Frontend Setup & Startup

Open a second PowerShell window in the project root:

```powershell
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Configure environment file
Copy-Item .env.example .env

# Start Vite dev server
npm run dev
```

Access the frontend application at **http://localhost:5173**.

---

### 3. Running Unit Tests & Production Build

```powershell
# Run backend pytest suite
$env:PYTHONPATH="backend"
python -m pytest backend/tests

# Run frontend production build
cd frontend
npm run build
```

---

## Verification Results & Limitations

- **Backend Unit Tests**: 11/11 tests passed successfully covering extraction, regex preprocessing, section parsing, mean-of-max scoring, relative fit score scaling, and API validation.
- **Frontend Production Build**: Vite bundle compiled cleanly with 0 errors.
- **Scanned PDFs**: Scanned PDF resumes without embedded text layer trigger an `ocr_warning` flag. An OCR engine (e.g. Tesseract) can be integrated for scanned document image parsing.
- **Human Review Disclaimer**: Relative similarity scores serve to assist human recruiters in shortlisting and do not replace final candidate verification.
