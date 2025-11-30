"""Tests for chat service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from search_api.chat_service import ChatResponse, ChatService
from search_api.meilisearch_client import SearchResult


@pytest.fixture
def mock_search_client() -> MagicMock:
    """Create mock search client."""
    return MagicMock()


@pytest.fixture
def mock_ollama() -> AsyncMock:
    """Create mock Ollama client."""
    return AsyncMock()


@pytest.fixture
def service(mock_search_client: MagicMock, mock_ollama: AsyncMock) -> ChatService:
    """Create chat service."""
    return ChatService(search_client=mock_search_client, ollama_client=mock_ollama)


@pytest.mark.asyncio
async def test_chat_with_results(
    service: ChatService, mock_search_client: MagicMock, mock_ollama: AsyncMock
) -> None:
    """Test chat when search returns results."""
    mock_search_client.search.return_value = [
        SearchResult(
            id="1",
            title="Python Guide",
            content="Python is a programming language",
            url="https://example.com/python",
        )
    ]
    mock_ollama.generate.return_value = "Python is a high-level programming language."

    response = await service.chat("What is Python?")

    assert response is not None
    assert "Python" in response.answer
    assert len(response.sources) == 1
    assert response.sources[0].url == "https://example.com/python"


@pytest.mark.asyncio
async def test_chat_no_results(
    service: ChatService, mock_search_client: MagicMock, mock_ollama: AsyncMock
) -> None:
    """Test chat when search returns no results."""
    mock_search_client.search.return_value = []
    mock_ollama.generate.return_value = "I don't have information about that."

    response = await service.chat("Unknown topic")

    assert response is not None
    assert len(response.sources) == 0
    assert "don't have information" in response.answer.lower()


@pytest.mark.asyncio
async def test_chat_uses_context(
    service: ChatService, mock_search_client: MagicMock, mock_ollama: AsyncMock
) -> None:
    """Test that chat uses search results as context."""
    mock_search_client.search.return_value = [
        SearchResult(
            id="1",
            title="Test",
            content="Specific context information",
            url="https://example.com",
        )
    ]
    mock_ollama.generate.return_value = "Answer based on context"

    await service.chat("test query")

    # Verify Ollama was called with context
    mock_ollama.generate.assert_called_once()
    call_args = mock_ollama.generate.call_args[0]
    prompt = call_args[0]
    assert "Specific context information" in prompt
