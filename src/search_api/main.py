"""FastAPI application for Search API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from search_api.chat_service import ChatResponse, ChatService
from search_api.config import settings
from search_api.meilisearch_client import MeilisearchClient
from search_api.ollama_client import OllamaClient
from search_api.models import SearchRequest, SearchResponse, SummarizeRequest, SummarizeResponse
from search_api.search_service import SearchService
from search_api.summarize_service import SummarizeService

# Create FastAPI app
app = FastAPI(
    title="Lookuply Search API",
    description="AI-powered search API with chat interface",
    version="0.1.0",
)

# CORS middleware (privacy-first: restrictive origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://lookuply.info"],
    allow_credentials=False,  # No cookies
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Initialize clients
search_client = MeilisearchClient(
    url=settings.meilisearch_url,
    api_key=settings.meilisearch_key,
    index=settings.meilisearch_index,
)

ollama_client = OllamaClient(
    base_url=settings.ollama_url,
    model=settings.ollama_model,
    timeout=settings.ollama_timeout,
)

search_service = SearchService(client=search_client)
summarize_service = SummarizeService(
    search_client=search_client, ollama_client=ollama_client
)
chat_service = ChatService(search_client=search_client, ollama_client=ollama_client)


class ChatRequest(BaseModel):
    """Chat request model."""

    query: str
    limit: int = 5


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"service": "Lookuply Search API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    # Check Meilisearch
    search_healthy = search_client.health_check()

    if not search_healthy:
        raise HTTPException(status_code=503, detail="Meilisearch unavailable")

    return {"status": "healthy", "search": "ok"}


@app.post("/api/search", response_model=SearchResponse)
async def search_sources(request: SearchRequest) -> SearchResponse:
    """
    Fast endpoint: Return relevant sources only (< 100ms)

    Does NOT generate AI answer - use /api/summarize for that
    Privacy: Does NOT log query or user data
    """
    try:
        sources = search_service.search(
            query=request.query, language=request.language, limit=request.limit
        )

        return SearchResponse(sources=sources)

    except Exception as e:
        raise HTTPException(status_code=503, detail="Search service unavailable")


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_answer(request: SummarizeRequest) -> SummarizeResponse:
    """
    Slow endpoint: Generate AI answer from sources (2-3s)

    Requires source_ids from /api/search
    Privacy: Does NOT log query or answer
    """
    try:
        answer = await summarize_service.generate_answer(
            query=request.query,
            language=request.language,
            source_ids=request.source_ids,
        )

        return SummarizeResponse(answer=answer, query_id=request.query_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate answer")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint for AI-powered search.

    Args:
        request: Chat request with query

    Returns:
        Chat response with answer and sources
    """
    if not request.query or len(request.query) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    if len(request.query) > 500:
        raise HTTPException(status_code=400, detail="Query too long")

    # Privacy: don't log user queries if disabled
    if not settings.log_user_queries:
        # Don't log the query content
        pass

    try:
        response = await chat_service.chat(request.query, limit=request.limit)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.on_event("shutdown")
async def shutdown() -> None:
    """Cleanup on shutdown."""
    await ollama_client.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
