from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import APP_NAME, STATIC_DIR, TEMPLATE_DIR
from app.schemas import CompareRequest, SearchRequest
from app.services.search_service import (
    ModelArtifactsMissingError,
    search_service,
)

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description=(
        "Semantic document retrieval using TF-IDF, Word2Vec, "
        "FastText, cosine similarity, and Top-K ranking."
    ),
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": APP_NAME},
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "models_ready": search_service.is_ready,
    }


@app.get("/api/models")
def models():
    return {
        "models": [
            {
                "id": "tfidf",
                "name": "TF-IDF",
                "description": "Lexical keyword baseline.",
            },
            {
                "id": "word2vec",
                "name": "Word2Vec",
                "description": "Dense semantic word embeddings.",
            },
            {
                "id": "fasttext",
                "name": "FastText",
                "description": "Subword embeddings with OOV robustness.",
            },
        ]
    }


@app.post("/api/search")
def search(request: SearchRequest):
    try:
        return search_service.search(
            query=request.query,
            model=request.model,
            top_k=request.top_k,
        )
    except ModelArtifactsMissingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/compare")
def compare(request: CompareRequest):
    try:
        return search_service.compare(
            query=request.query,
            top_k=request.top_k,
        )
    except ModelArtifactsMissingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
