from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""

class EvidenceItem(BaseModel):
    jd_chunk: str
    resume_chunk: str
    resume_section: str
    sim: float

class CandidateResult(BaseModel):
    rank: int
    file_name: str
    candidate_name: Optional[str] = None
    fit_score: Optional[float] = Field(None, description="Min-max scaled score (0-100) within the candidate pool")
    raw_score: Optional[float] = Field(None, description="Average cosine similarity across matched sections")
    contact: ContactInfo
    sections_found: List[str]
    used_fallback: bool
    section_scores: Dict[str, Optional[float]]
    evidence: Dict[str, List[EvidenceItem]]
    ner_entities: Dict[str, List[str]] = {}
    ocr_warning: bool = False
    unscored: bool = False
    unscored_reason: Optional[str] = None

class FileError(BaseModel):
    file_name: str
    error: str

class ScreeningResponse(BaseModel):
    total_resumes_processed: int
    successful_count: int
    failed_count: int
    jd_sections_detected: List[str]
    jd_used_fallback: bool
    shortlist: List[CandidateResult]
    unscored_resumes: List[CandidateResult] = []
    file_errors: List[FileError] = []
    disclaimer: str = "Similarity scores support human review and do not guarantee that every job requirement is satisfied."

class HealthStatus(BaseModel):
    status: str
    models_loaded: bool
    device: str
    embedding_model: str
    ner_model: str
    message: str
