"""Meilisearch client for search operations."""

from typing import Any

import meilisearch
from pydantic import BaseModel


class SearchResult(BaseModel):
    """Search result from Meilisearch."""

    id: str
    title: str
    content: str
    url: str
    score: float = 0.0


class MeilisearchClient:
    """Client for Meilisearch operations."""

    def __init__(self, url: str, api_key: str, index: str) -> None:
        """Initialize Meilisearch client.

        Args:
            url: Meilisearch server URL
            api_key: API key for authentication
            index: Index name to use
        """
        self.client = meilisearch.Client(url, api_key)
        self.index = self.client.index(index)

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search for documents.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of search results
        """
        response = self.index.search(query, {"limit": limit, "showRankingScore": True})

        results = []
        for hit in response.get("hits", []):
            result = SearchResult(
                id=str(hit.get("id", "")),
                title=hit.get("title", ""),
                content=hit.get("content", ""),
                url=hit.get("url", ""),
                score=hit.get("_rankingScore", 0.0),
            )
            results.append(result)

        return results

    def index_document(self, document: dict[str, Any]) -> None:
        """Index a document.

        Args:
            document: Document to index
        """
        self.index.add_documents([document])

    def health_check(self) -> bool:
        """Check if Meilisearch is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            health = self.client.health()
            return health.get("status") == "available"
        except Exception:
            return False
