"""schemas.py -- Pydantic request/response models: the API contract."""
from typing import List, Optional
from pydantic import BaseModel, Field


class SourceOut(BaseModel):
    doc_name: str
    page_number: int
    unit_label: str = "Page"


class DocumentsListResponse(BaseModel):
    documents: List[str]
    chunk_count: int


class UploadFileResult(BaseModel):
    filename: str
    status: str  # "ok" | "skipped" | "error"
    detail: str
    chunks_indexed: Optional[int] = None


class UploadResponse(BaseModel):
    results: List[UploadFileResult]
    documents: List[str]
    chunk_count: int


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceOut]
    grounded: bool


class TestRequest(BaseModel):
    questions: Optional[List[str]] = None  # falls back to DEFAULT_TEST_QUESTIONS if omitted


class TestCaseOut(BaseModel):
    question: str
    num_chunks_retrieved: int
    top_distance: Optional[float] = None
    answer: str
    sources: List[SourceOut]
    grounded: bool


class TestResponse(BaseModel):
    results: List[TestCaseOut]


class DefaultQuestionsResponse(BaseModel):
    questions: List[str]
