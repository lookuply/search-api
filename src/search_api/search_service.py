"""
Search service - handles Meilisearch queries
Single Responsibility: Search index interaction only
"""

import logging
from typing import List

from search_api.meilisearch_client import MeilisearchClient, SearchResult
from search_api.models import Source

logger = logging.getLogger(__name__)


class SearchService:
    """
    Handles search index queries (Meilisearch)

    SOLID: Single Responsibility - only searches, doesn't generate answers
    """

    def __init__(self, client: MeilisearchClient):
        self.client = client

    def search(self, query: str, language: str = "en", limit: int = 10) -> List[Source]:
        """
        Search Meilisearch index for relevant pages

        Privacy: Does NOT log query or user data
        Performance: Must complete in < 100ms

        Args:
            query: User search query (NOT logged)
            language: Target language
            limit: Max results to return

        Returns:
            List of relevant sources with scores
        """
        try:
            # Query Meilisearch (fast!)
            results: List[SearchResult] = self.client.search(query, limit=limit)

            # Transform to Source objects
            sources = []
            for result in results:
                snippet = self._extract_snippet(result.content)

                sources.append(
                    Source(
                        id=result.id,
                        title=result.title,
                        url=result.url,
                        snippet=snippet,
                        relevance_score=result.score,
                    )
                )

            # DO NOT LOG QUERY (privacy!)
            logger.info(f"Search completed: {len(sources)} results found")

            # Sort by relevance score (descending)
            sources.sort(key=lambda s: s.relevance_score, reverse=True)

            # Enforce limit (defense in depth, in case Meilisearch returns more)
            return sources[:limit]

        except Exception as e:
            logger.error(f"Meilisearch error: {type(e).__name__}")
            raise

    def _extract_snippet(self, content: str, max_length: int = 200) -> str:
        """Extract snippet from content (truncate if needed)"""
        if not content:
            return ""

        # Truncate to max_length
        if len(content) > max_length:
            return content[:max_length] + "..."

        return content
