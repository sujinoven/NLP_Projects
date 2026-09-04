from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .recommender import FastTextRecommender
from .schemas import Product, RecommendationResponse


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
recommender = FastTextRecommender(DATA_DIR if DATA_DIR.exists() else BASE_DIR / "artifacts")

app = FastAPI(
    title="Acme Product Recommendation API",
    description="FastText-powered product similarity search",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Acme Product Recommendation API", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {
        "status": "ready" if recommender.ready else "waiting_for_artifacts",
        "products": len(recommender.products) if recommender.products is not None else 0,
        "detail": recommender.error,
    }


@app.get("/api/products/search", response_model=list[Product])
def search_products(query: str = Query(min_length=2), limit: int = Query(8, ge=1, le=20)):
    try:
        return recommender.search_products(query, limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/recommendations", response_model=RecommendationResponse)
def recommendations(query: str = Query(min_length=2), limit: int = Query(8, ge=1, le=20)):
    try:
        selected, products = recommender.recommend(query, limit)
        return RecommendationResponse(
            selected_product=selected,
            recommendations=products,
            message=f"Top {len(products)} FastText matches",
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
