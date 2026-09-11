Build a complete full-stack Resume Screening application using the attached Jupyter notebook as the source of truth.

First inspect the notebook and existing project folder. Understand the processing pipeline before implementing it. Preserve existing files and follow any established folder structure. If no structure exists, use the layout below.

Use:
- Frontend: React with Vite and Tailwind CSS.
- Backend: Python FastAPI.
- Models and processing: the libraries and models used in the notebook.
- Local development: Windows-compatible commands.

Keep the implementation simple, readable, and modular.

PROJECT STRUCTURE

resume-screening/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── .env.example
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── services/
│   │   │   ├── extraction.py
│   │   │   ├── preprocessing.py
│   │   │   ├── sections.py
│   │   │   ├── embeddings.py
│   │   │   ├── scoring.py
│   │   │   └── entities.py
│   │   ├── schemas.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── notebooks/
├── .gitignore
└── README.md

NOTEBOOK CONVERSION

1. Convert notebook functions into reusable backend modules.
2. Remove Google Colab drive mounting, notebook installation commands,
   display() calls, and hardcoded Google Drive paths.
3. Keep the original notebook under notebooks/ without overwriting it.
4. Preserve original resume text for NER and contact extraction.
5. Use cleaned text for section splitting and semantic matching.
6. Support PDF, DOCX, and TXT resumes.
7. Support pasting a JD or uploading a PDF, DOCX, or TXT JD.
8. Preserve the notebook's section mappings, chunking, embedding,
   mean-of-max scoring, and evidence extraction.
9. Use the notebook's models:
   - BAAI/bge-large-en-v1.5
   - yashpwr/resume-ner-bert
10. Load models once per backend process and reuse them. Support CPU
    and GPU automatically. Show a useful status while models load.
11. Inspect actual NER labels before implementing name selection.
    Do not treat company-name labels as candidate names.
12. Preserve the JD query prefix and normalized embeddings.

SCORING AND EDGE CASES

- Inspect how raw_score is calculated in the notebook. Preserve that
  calculation if present.
- If it is missing, use the equal-weight average of available,
  non-missing section scores and document this choice.
- A resume with no valid comparisons must be shown as unscored and
  excluded from the ranked shortlist.
- Preserve raw scores and section scores for inspection.
- Label min-max fit_score as "Relative score", not "Match percentage".
  Explain that it depends on the uploaded candidate pool.
- Handle identical scores, one resume, empty input, missing sections,
  JD full-text fallback, and resume full-text fallback explicitly.
- If JD fallback prevents section-wise scoring, return a clear
  explanation instead of silently producing an empty ranking.
- Do not invent experience years. If years extraction is absent,
  omit the field or show "Not extracted"; never assume zero.
- Do not add ranking criteria based on names or contact information.
- Detect empty text extraction and report that scanned PDFs may need
  OCR. Do not silently rank an empty resume.
- Handle malformed files individually so one failure does not discard
  the other uploaded resumes.
- Keep uploaded files isolated per request and clean up temporary files.
- Use safe server-generated filenames and configurable upload limits.
- Respect model token limits and avoid silent loss of long input.

USER INTERFACE

Create a polished, responsive interface with:
- JD text input and file upload.
- Multiple resume uploads with a list of selected files.
- Configurable shortlist size, defaulting to five.
- A clear "Screen resumes" button.
- Honest loading and error states; do not simulate progress.
- A results table with rank, filename, candidate name when available,
  relative score, and raw similarity.
- Expandable candidate details showing section scores and matching
  JD/resume evidence with source section and similarity.
- Contact details extracted from original resume text.
- An explanation that similarity supports human review and does not
  verify that every job requirement is satisfied.
- CSV download of the displayed results.

Do not show fake candidates or hardcoded scores as real results.
Keep model names and implementation details out of the main user flow.

API

Provide:
- A lightweight health/status endpoint.
- A screening endpoint accepting multipart file uploads and JD input.
- Structured response schemas for results, evidence, and per-file errors.

Configure the frontend API URL through environment variables and
restrict development CORS to the configured frontend origin.
Prevent long inference from blocking lightweight health requests.

GIT HYGIENE

Create a root .gitignore covering:
- node_modules/
- dist/ and build/
- .venv/ and venv/
- __pycache__/ and *.py[cod]
- .pytest_cache/ and .ipynb_checkpoints/
- .env and .env.* while allowing .env.example
- logs, coverage output, and OS temporary files
- runtime uploads, extracted resume data, and generated result exports
- local model caches and downloaded model weights

Do not ignore application source code or dependency lockfiles.
Do not commit resumes, contact data, secrets, notebook outputs containing
personal information, or model weights.
Preserve existing Git history. Do not push or deploy without my request.

VALIDATION AND DELIVERY

Implement the app, rather than only describing a plan.

Test meaningful behavior:
- Supported file extraction.
- Section splitting and fallback handling.
- Mean-of-max scoring.
- Missing scores and identical-score scaling.
- API validation and malformed uploads.

Run the frontend production build and backend tests.
Where possible, run one real end-to-end inference with synthetic resume
data. Clearly distinguish mocked tests from real model inference.
If model downloads or hardware prevent inference, state exactly what
remains unverified.

Write a README with exact Windows PowerShell commands for:
1. Creating and activating the backend virtual environment.
2. Installing backend dependencies.
3. Configuring environment files.
4. Starting FastAPI.
5. Installing and starting the frontend.
6. Running tests and the frontend build.

Mention first-run model downloads and CPU performance expectations.

Finish with a concise summary of implemented features, folder structure,
verification results, and any remaining limitations.