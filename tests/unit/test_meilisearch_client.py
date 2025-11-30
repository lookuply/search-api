"""Tests for Meilisearch client."""

from unittest.mock import MagicMock

import pytest

from search_api.meilisearch_client import MeilisearchClient, SearchResult


@pytest.fixture
def client() -> MeilisearchClient:
    """Create Meilisearch client."""
    return MeilisearchClient(url="http://test:7700", api_key="test_key", index="pages")


def test_search_success(client: MeilisearchClient) -> None:
    """Test successful search."""
    mock_index = MagicMock()
    mock_index.search.return_value = {
        "hits": [
            {"id": "1", "title": "Test Page", "content": "Test content", "url": "https://example.com"},
        ],
        "estimatedTotalHits": 1,
    }
    client.index = mock_index

    results = client.search("test query")

    assert len(results) == 1
    assert results[0].title == "Test Page"
    assert results[0].url == "https://example.com"


def test_search_empty_results(client: MeilisearchClient) -> None:
    """Test search with no results."""
    mock_index = MagicMock()
    mock_index.search.return_value = {"hits": [], "estimatedTotalHits": 0}
    client.index = mock_index

    results = client.search("nonexistent query")

    assert len(results) == 0


def test_search_with_limit(client: MeilisearchClient) -> None:
    """Test search with limit."""
    mock_index = MagicMock()
    mock_index.search.return_value = {"hits": [{"id": str(i)} for i in range(20)], "estimatedTotalHits": 20}
    client.index = mock_index

    results = client.search("test", limit=5)

    assert len(results) <= 5
    mock_index.search.assert_called_once()
    call_kwargs = mock_index.search.call_args.kwargs
    assert call_kwargs.get("limit") == 5


def test_index_document(client: MeilisearchClient) -> None:
    """Test indexing a document."""
    mock_index = MagicMock()
    client.index = mock_index

    doc = {"id": "1", "title": "Test", "content": "Content", "url": "https://example.com"}
    client.index_document(doc)

    mock_index.add_documents.assert_called_once_with([doc])


def test_health_check_success(client: MeilisearchClient) -> None:
    """Test health check when Meilisearch is healthy."""
    mock_client = MagicMock()
    mock_client.health.return_value = {"status": "available"}
    client.client = mock_client

    result = client.health_check()

    assert result is True


def test_health_check_failure(client: MeilisearchClient) -> None:
    """Test health check when Meilisearch is unavailable."""
    mock_client = MagicMock()
    mock_client.health.side_effect = Exception("Connection failed")
    client.client = mock_client

    result = client.health_check()

    assert result is False
