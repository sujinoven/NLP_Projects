import pytest
from app.services.scoring import calculate_raw_score, compute_relative_scores

def test_calculate_raw_score():
    scores = {"required_skills": 0.8, "experience": 0.6, "responsibilities": None}
    raw = calculate_raw_score(scores)
    assert raw == pytest.approx(0.7)

def test_compute_relative_scores():
    candidates = [
        {"raw_score": 0.85},
        {"raw_score": 0.65},
        {"raw_score": 0.75}
    ]
    results = compute_relative_scores(candidates)
    fit_scores = [c["fit_score"] for c in results]
    assert fit_scores[0] == 100.0
    assert fit_scores[1] == 0.0
    assert fit_scores[2] == 50.0

def test_compute_relative_scores_single_candidate():
    candidates = [{"raw_score": 0.78}]
    results = compute_relative_scores(candidates)
    assert results[0]["fit_score"] == 50.0
