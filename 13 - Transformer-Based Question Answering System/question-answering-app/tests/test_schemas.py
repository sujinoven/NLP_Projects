import pytest
from pydantic import ValidationError
from app.schemas import QARequest, QAResponse, HealthResponse


def test_valid_qa_request():
    req = QARequest(
        context="  DistilBERT is a fast model.  ",
        question="  What is DistilBERT?  "
    )
    assert req.context == "DistilBERT is a fast model."
    assert req.question == "What is DistilBERT?"


def test_empty_context_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        QARequest(context="   ", question="What is BERT?")
    assert "Context passage cannot be empty" in str(exc_info.value)


def test_empty_question_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        QARequest(context="Some valid context text.", question="   ")
    assert "Question cannot be empty" in str(exc_info.value)


def test_oversized_context_raises_validation_error():
    long_context = "A" * 10001
    with pytest.raises(ValidationError) as exc_info:
        QARequest(context=long_context, question="Question?")
    assert "exceeds maximum allowed length of 10,000 characters" in str(exc_info.value)


def test_oversized_question_raises_validation_error():
    long_question = "Q" * 501
    with pytest.raises(ValidationError) as exc_info:
        QARequest(context="Valid context.", question=long_question)
    assert "exceeds maximum allowed length of 500 characters" in str(exc_info.value)


def test_valid_qa_response_schema():
    resp = QAResponse(
        answer="fast model",
        start_char=16,
        end_char=26,
        score=4.52,
        context_length=27
    )
    assert resp.answer == "fast model"
    assert resp.start_char == 16
    assert resp.end_char == 26
    assert resp.score == 4.52


def test_valid_health_response_schema():
    health = HealthResponse(
        status="healthy",
        model_loaded=True,
        model_path="/path/to/model",
        device="cpu",
        message="All systems operational"
    )
    assert health.status == "healthy"
    assert health.model_loaded is True
