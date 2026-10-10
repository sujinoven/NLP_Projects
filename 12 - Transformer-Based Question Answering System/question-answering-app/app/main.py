from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import QARequest, QAResponse, HealthResponse
from app.qa_service import QAService

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Instantiate service
qa_service = QAService(model_dir=MODEL_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to load model on startup."""
    qa_service.load_model()
    yield


app = FastAPI(
    title="DistilBERT Question Answering AI System",
    description="Extractive QA API powered by fine-tuned DistilBERT on SQuAD v1.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory if it exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def serve_index():
    """Serve main single-page web UI."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend index.html not found."
        )
    return FileResponse(index_file)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health and local model status."""
    if qa_service.is_loaded:
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            model_path=str(qa_service.model_dir.absolute()),
            device=str(qa_service.device),
            message="DistilBERT QA model is loaded and operational."
        )
    else:
        return HealthResponse(
            status="model_missing",
            model_loaded=False,
            model_path=str(qa_service.model_dir.absolute()),
            device=str(qa_service.device),
            message=qa_service.load_error or "Model weights not found."
        )


@app.post("/api/answer", response_model=QAResponse)
async def answer_question(request: QARequest):
    """Extract answer span from provided context and question."""
    if not qa_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_531_SERVICE_UNAVAILABLE if hasattr(status, "HTTP_531_SERVICE_UNAVAILABLE") else 503,
            detail=qa_service.load_error or "Model is not loaded. Please ensure distilbert_squad_model is extracted in model/ directory."
        )

    try:
        result = qa_service.answer_question(
            context=request.context,
            question=request.question
        )
        return QAResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
