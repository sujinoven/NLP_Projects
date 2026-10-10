from fastapi.testclient import TestClient
from app.main import app, qa_service

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "model_path" in data
    assert "device" in data


def test_answer_endpoint_validation_error():
    # Missing required question field
    response = client.post("/api/answer", json={"context": "Some context."})
    assert response.status_code == 422

    # Empty context field
    response = client.post("/api/answer", json={"context": "   ", "question": "Question?"})
    assert response.status_code == 422


def test_answer_endpoint_unloaded_model_behavior():
    # Temporarily set qa_service loaded state to False
    original_state = qa_service.is_loaded
    qa_service.is_loaded = False
    qa_service.load_error = "Model weights not loaded for test."

    response = client.post("/api/answer", json={
        "context": "DistilBERT is a distilled version of BERT.",
        "question": "What is DistilBERT?"
    })

    # Restore state
    qa_service.is_loaded = original_state

    assert response.status_code == 503
    assert "not loaded" in response.json()["detail"].lower()
