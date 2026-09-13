from pydantic import BaseModel, Field, field_validator


class QARequest(BaseModel):
    """Request schema for question answering endpoint."""
    context: str = Field(
        ...,
        description="The passage of context text from which the answer should be extracted.",
        examples=["DistilBERT is a small, fast, cheap and light Transformer model trained by distilling BERT base."]
    )
    question: str = Field(
        ...,
        description="The question to be answered using the provided context.",
        examples=["What is DistilBERT?"]
    )

    @field_validator("context")
    @classmethod
    def validate_context(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Context passage cannot be empty or contain only whitespace.")
        if len(v_stripped) > 10000:
            raise ValueError("Context passage exceeds maximum allowed length of 10,000 characters.")
        return v_stripped

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Question cannot be empty or contain only whitespace.")
        if len(v_stripped) > 500:
            raise ValueError("Question exceeds maximum allowed length of 500 characters.")
        return v_stripped


class QAResponse(BaseModel):
    """Response schema for question answering endpoint."""
    answer: str = Field(..., description="Extracted answer text from the context.")
    start_char: int = Field(..., description="0-based starting character index in the original context.")
    end_char: int = Field(..., description="0-based ending character index (exclusive) in the original context.")
    score: float = Field(..., description="Combined start + end logit score from model inference.")
    context_length: int = Field(..., description="Total length of context string.")


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str = Field(..., description="System health status ('healthy' or 'model_missing').")
    model_loaded: bool = Field(..., description="Whether the local DistilBERT model is loaded and ready.")
    model_path: str = Field(..., description="Path to the model directory.")
    device: str = Field(..., description="Computation device being used (e.g. 'cpu').")
    message: str = Field(..., description="Descriptive status message.")
