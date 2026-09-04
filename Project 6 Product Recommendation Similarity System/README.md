# Acme Product Recommendation System

FastText product recommendations with a FastAPI backend and React frontend.

## Model files

Place these Colab exports in the project-level `data` folder:

- `prepared_products.csv`
- `fasttext_product_vectors.npy`
- `fasttext.model` and any FastText sidecar files

The CSV and vector rows must remain in the same order.

## Run the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Run the frontend

In a second terminal:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.
