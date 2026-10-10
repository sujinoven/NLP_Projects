import pytest
from pydantic import ValidationError

from app.schemas import SearchRequest


def test_valid_search_request():
    request = SearchRequest(
        query="forgot password",
        model="fasttext",
        top_k=5,
    )
    assert request.top_k == 5


def test_blank_query_is_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(
            query="   ",
            model="tfidf",
            top_k=5,
        )
