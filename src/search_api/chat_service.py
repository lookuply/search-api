"""Chat service combining search and LLM."""

from pydantic import BaseModel

from search_api.meilisearch_client import MeilisearchClient, SearchResult
from search_api.ollama_client import OllamaClient


class Source(BaseModel):
    """Source citation for answer."""

    title: str
    url: str
    snippet: str


class ChatResponse(BaseModel):
    """Response from chat service."""

    answer: str
    sources: list[Source]
    query: str


class ChatService:
    """Service for chat-based search with AI answers."""

    def __init__(self, search_client: MeilisearchClient, ollama_client: OllamaClient) -> None:
        """Initialize chat service."""
        self.search = search_client
        self.ollama = ollama_client

    async def chat(self, query: str, limit: int = 5) -> ChatResponse:
        """Process chat query.

        Args:
            query: User query
            limit: Max search results to use

        Returns:
            Chat response with answer and sources
        """
        # Search for relevant pages
        results = self.search.search(query, limit=limit)

        # Build context from search results
        context = self._build_context(results)

        # Generate answer using LLM
        if context:
            system_prompt = """You are a helpful search assistant. Answer the user's question
based on the provided context. If the context doesn't contain enough information,
say so. Always cite your sources."""

            user_prompt = f"""Context from search results:
{context}

User question: {query}

Please provide a helpful answer based on the context above."""

            answer = await self.ollama.generate(user_prompt, system=system_prompt)
        else:
            answer = "I don't have enough information to answer that question."

        # Build sources list
        sources = [
            Source(title=r.title, url=r.url, snippet=r.content[:200])
            for r in results[:3]  # Top 3 sources
        ]

        return ChatResponse(answer=answer, sources=sources, query=query)

    def _build_context(self, results: list[SearchResult]) -> str:
        """Build context string from search results."""
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result.title}")
            context_parts.append(f"URL: {result.url}")
            context_parts.append(f"{result.content[:500]}")
            context_parts.append("")

        return "\n".join(context_parts)
