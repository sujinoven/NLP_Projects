"""
Unit & Integration Tests for Legal Clause Similarity Engine Backend
====================================================================

Tests cover:
1. Root endpoint GET /
2. Health check endpoint GET /health
3. Search endpoint POST /search with valid legal clause
4. Search endpoint error handling with empty input
5. Search endpoint error handling with unknown words outside model vocabulary
6. Search endpoint with custom top_k parameter
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint status message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Legal Clause Similarity Engine API is running." in data["message"]


def test_check_health():
    """Test the health check endpoint for dataset stats."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["clauses"] > 0
    assert data["vector_size"] == 100


def test_search_valid_clause():
    """Test POST /search with a standard legal clause."""
    payload = {
        "clause": "The tenant shall pay monthly rent before the fifth day of each month.",
        "top_k": 5
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "query" in data
    assert "processed_tokens" in data
    assert "results" in data
    assert len(data["results"]) == 5
    
    # Verify rank 1 result structure
    top_result = data["results"][0]
    assert top_result["rank"] == 1
    assert "clause_text" in top_result
    assert "clause_type" in top_result
    assert "similarity_score" in top_result
    assert 0.0 <= top_result["similarity_score"] <= 1.0


def test_search_empty_clause():
    """Test POST /search error handling for empty clause string."""
    payload = {
        "clause": "   ",
        "top_k": 5
    }
    response = client.post("/search", json=payload)
    # Pydantic or app returns error response
    assert response.status_code in [200, 422]
    data = response.json()
    if response.status_code == 200:
        assert "error" in data
    else:
        assert "detail" in data


def test_search_unknown_words():
    """Test POST /search when clause contains only words outside vocabulary."""
    payload = {
        "clause": "xyzqwert12345 nonesenseword",
        "top_k": 5
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "vocabulary" in data["error"].lower()


def test_search_custom_top_k():
    """Test POST /search with custom top_k count of 3."""
    payload = {
        "clause": "The party shall maintain confidentiality of all proprietary information.",
        "top_k": 3
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3
