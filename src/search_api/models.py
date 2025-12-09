"""
Pydantic models for API requests/responses
"""

from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """Request model for /api/search"""

    query: str = Field(..., min_length=1, max_length=500)
    language: str = Field(..., pattern="^(en|sk|de)$")
    limit: int = Field(default=10, ge=1, le=50)

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        """Ensure query is not empty or whitespace only"""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class Source(BaseModel):
    """Single search result source"""

    id: str
    title: str
    url: str
    snippet: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Response model for /api/search"""

    sources: list[Source]
    query_id: str = Field(default_factory=lambda: str(uuid4()))


class SummarizeRequest(BaseModel):
    """Request model for /api/summarize"""

    query: str = Field(..., min_length=1, max_length=500)
    language: str = Field(..., pattern="^(en|sk|de)$")
    query_id: str
    source_ids: list[str] = Field(..., min_length=1)

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        """Ensure query is not empty or whitespace only"""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SummarizeResponse(BaseModel):
    """Response model for /api/summarize"""

    answer: str
    query_id: str
