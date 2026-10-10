from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "embedding_model" in data
    assert "ner_model" in data

def test_screen_endpoint_validation():
    # Test missing JD text and file
    response = client.post("/api/screen")
    assert response.status_code == 422 # FastAPI validation error for missing required resumes field
