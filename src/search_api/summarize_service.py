"""
Summarize service - handles LLM answer generation
Single Responsibility: AI answer generation only
"""

import logging
from typing import List

from search_api.meilisearch_client import MeilisearchClient, SearchResult
from search_api.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class SummarizeService:
    """
    Generates AI answers from sources using LLM

    SOLID: Single Responsibility - only generates answers
    SOLID: Dependency Injection - clients injected
    """

    def __init__(
        self, search_client: MeilisearchClient, ollama_client: OllamaClient
    ):
        self.search_client = search_client
        self.ollama = ollama_client

    async def generate_answer(
        self, query: str, language: str, source_ids: List[str]
    ) -> str:
        """
        Generate AI answer using LLM and source content

        Privacy: Does NOT log query or answer
        Performance: May take 2-3s (LLM processing)

        Args:
            query: User question (NOT logged)
            language: Target language for answer
            source_ids: IDs of sources to use for context

        Returns:
            AI-generated answer string

        Raises:
            Exception: If LLM generation fails
        """
        try:
            # 1. Fetch source content by searching for all sources
            # We search with a broad query to get all indexed content
            # Then filter by IDs
            all_results = self.search_client.search("", limit=100)

            # Filter to only requested source IDs
            sources = [r for r in all_results if r.id in source_ids]

            if not sources:
                # Fallback: no sources found
                logger.warning(f"No sources found for IDs: {source_ids}")
                return "I don't have enough information to answer that question."

            # 2. Build context from sources
            context = self._build_context(sources)

            # 3. Generate answer with LLM
            prompt = self._build_prompt(query, context, language)

            system_prompt = """You are a helpful search assistant. Answer the user's question based ONLY on the provided sources. Be concise and accurate."""

            answer = await self.ollama.generate(prompt, system=system_prompt)

            # DO NOT LOG QUERY OR ANSWER (privacy!)
            logger.info("Answer generated successfully")

            return answer.strip()

        except Exception as e:
            logger.error(f"Summarize error: {type(e).__name__}")
            raise

    def _build_context(self, sources: List[SearchResult]) -> str:
        """Build context string from source content"""
        context_parts = []

        for i, source in enumerate(sources, 1):
            context_parts.append(f"Source {i} ({source.title}):")
            context_parts.append(f"URL: {source.url}")
            context_parts.append(f"{source.content[:500]}")  # Limit context length
            context_parts.append("")

        return "\n".join(context_parts)

    def _build_prompt(self, query: str, context: str, language: str) -> str:
        """Build LLM prompt with query and context"""
        lang_names = {"en": "English", "sk": "Slovak", "de": "German"}
        lang_name = lang_names.get(language, "English")

        return f"""You are a helpful search assistant. Answer the user's question based ONLY on the provided sources.

Sources:
{context}

User Question: {query}

Instructions:
- Answer in {lang_name}
- Use only information from the sources
- Be concise and accurate (2-3 paragraphs maximum)
- If sources don't contain the answer, say so
- Do not make up information

Answer:"""
