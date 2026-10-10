# Semantic Similarity Search System

A modular NLP search application built with **FastAPI**, **TF-IDF**, **Word2Vec**, and **FastText**.

The project supports:

- Consistent text cleaning and preprocessing
- TF-IDF lexical baseline
- Word2Vec semantic retrieval
- FastText semantic retrieval with subword/OOV support
- Cosine similarity ranking
- User-selectable Top-K results
- FastAPI backend
- Responsive browser UI
- Model comparison endpoint
- Modular training and inference code

## Project structure

```text
semantic_similarity_fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── preprocessing.py
│   │   └── search_service.py
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   └── templates/
│       └── index.html
├── data/
│   └── README.md
├── models/
│   └── .gitkeep
├── scripts/
│   ├── evaluate_models.py
│   └── train_models.py
├── tests/
│   ├── test_preprocessing.py
│   └── test_schema.py
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## 1. Setup

Open the extracted folder in VS Code.

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Add the dataset

Copy your original dataset into:

```text
data/knowledge_base.csv
```

Expected columns:

```text
document_id, category, title, content, keywords
```

## 3. Train and save the models

```bash
python scripts/train_models.py
```

This creates reusable model artifacts in `models/`.

Expected artifacts include:

```text
models/documents.pkl
models/tfidf_vectorizer.pkl
models/tfidf_matrix.npz
models/word2vec.model
models/word2vec_vectors.npy
models/fasttext.model
models/fasttext_vectors.npy
models/model_metadata.json
```

## 4. Run the FastAPI app

```bash
python run.py
```

or:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## API examples

### Search

`POST /api/search`

```json
{
  "query": "I forgot my password and cannot login",
  "model": "fasttext",
  "top_k": 5
}
```

Available models:

- `tfidf`
- `word2vec`
- `fasttext`

### Compare all models

`POST /api/compare`

```json
{
  "query": "I cannot get into my account anymore",
  "top_k": 5
}
```

## Model notes

### TF-IDF

Represents documents with sparse term-weight vectors. It is a strong lexical baseline when query wording overlaps with the knowledge base.

### Word2Vec

Learns dense word embeddings from context. Document and query vectors are created by averaging known word vectors. OOV words are ignored.

### FastText

Extends word embeddings with character subword information. It can construct vectors for unseen words, making it more robust to misspellings and OOV terms.

## Evaluation

The included evaluation script calculates category-based Precision@K.

```bash
python scripts/evaluate_models.py
```

Category membership is used as a proxy for relevance, so the metric should be interpreted as an approximate retrieval-quality measure rather than a perfect human relevance judgment.

## Notes for submission

Recommended deliverables:

- Source code
- README
- Report
- Screenshots of the UI and API
- Short demonstration video
- Example comparisons across TF-IDF, Word2Vec, and FastText
