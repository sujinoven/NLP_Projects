from typing import Literal
from pydantic import BaseModel, Field, field_validator

ModelName = Literal["tfidf", "word2vec", "fasttext"]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    model: ModelName = "fasttext"
    top_k: int = Field(default=5, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be blank.")
        return value


class CompareRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be blank.")
        return value
