"""
Test suite for /api/search endpoint (sources only)
TDD: Write tests FIRST, then implement
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from search_api.main import app
from search_api.meilisearch_client import SearchResult

client = TestClient(app)


@pytest.fixture
def mock_search_results():
    """Mock search results from Meilisearch."""
    return [
        SearchResult(
            id="1",
            title="Quantum Computing Explained",
            url="https://example.com/quantum",
            content="Quantum computing uses quantum mechanics...",
            score=0.95,
        ),
        SearchResult(
            id="2",
            title="Introduction to Quantum Physics",
            url="https://example.com/quantum-intro",
            content="Quantum physics is the study of...",
            score=0.87,
        ),
        SearchResult(
            id="3",
            title="Quantum Computers Today",
            url="https://example.com/quantum-today",
            content="Modern quantum computers are...",
            score=0.82,
        ),
    ]


class TestSearchEndpoint:
    """Test /api/search returns sources quickly without AI"""

    def test_search_returns_sources_only(self, mock_search_results):
        """Should return sources without AI-generated answer"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            response = client.post(
                "/api/search", json={"query": "quantum computing", "language": "en"}
            )

            assert response.status_code == 200
            data = response.json()

            # Must have sources
            assert "sources" in data
            assert isinstance(data["sources"], list)
            assert len(data["sources"]) > 0

            # Must NOT have answer (that's for /api/summarize)
            assert "answer" not in data

            # Must have query_id for tracking
            assert "query_id" in data
            assert isinstance(data["query_id"], str)
            assert len(data["query_id"]) > 0

    def test_search_source_structure(self, mock_search_results):
        """Each source must have required fields"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            response = client.post(
                "/api/search", json={"query": "python programming", "language": "en"}
            )

            assert response.status_code == 200
            source = response.json()["sources"][0]

            # Required fields
            assert "id" in source
            assert "title" in source
            assert "url" in source
            assert "snippet" in source
            assert "relevance_score" in source

            # Type validation
            assert isinstance(source["id"], str)
            assert isinstance(source["title"], str)
            assert isinstance(source["url"], str)
            assert isinstance(source["snippet"], str)
            assert isinstance(source["relevance_score"], float)
            assert 0.0 <= source["relevance_score"] <= 1.0

    def test_search_empty_query(self):
        """Should reject empty queries"""
        response = client.post(
            "/api/search", json={"query": "", "language": "en"}
        )

        assert response.status_code == 422  # Validation error

    def test_search_missing_query(self):
        """Should reject missing query field"""
        response = client.post("/api/search", json={"language": "en"})

        assert response.status_code == 422  # Validation error

    def test_search_invalid_language(self):
        """Should reject invalid language codes"""
        response = client.post(
            "/api/search", json={"query": "test", "language": "invalid"}
        )

        assert response.status_code == 422  # Validation error

    def test_search_valid_languages(self, mock_search_results):
        """Should accept valid language codes (en, sk, de)"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            for lang in ["en", "sk", "de"]:
                response = client.post(
                    "/api/search", json={"query": "test", "language": lang}
                )
                assert response.status_code == 200, f"Language {lang} should be valid"

    def test_search_no_results(self):
        """Should return empty list if no results found"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = []  # No results

            response = client.post(
                "/api/search", json={"query": "xyzabc123nonexistent", "language": "en"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["sources"] == []
            assert "query_id" in data  # Still return query_id

    def test_search_pagination(self, mock_search_results):
        """Should support limit parameter"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            response = client.post(
                "/api/search", json={"query": "python", "language": "en", "limit": 2}
            )

            assert response.status_code == 200
            sources = response.json()["sources"]
            assert len(sources) <= 2

    def test_search_default_limit(self, mock_search_results):
        """Should use default limit of 10 if not specified"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            response = client.post(
                "/api/search", json={"query": "python", "language": "en"}
            )

            assert response.status_code == 200
            # Check that search was called with default limit
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            # limit should be in kwargs or default to 10
            limit = call_args.kwargs.get("limit", 10)
            assert limit == 10

    def test_search_max_limit(self, mock_search_results):
        """Should enforce maximum limit of 50"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            response = client.post(
                "/api/search", json={"query": "test", "language": "en", "limit": 100}
            )

            # Should reject or cap at 50
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                # If accepted, check it was capped
                call_args = mock_search.call_args
                limit = call_args.kwargs.get("limit", 10)
                assert limit <= 50

    def test_search_query_length_validation(self):
        """Should validate query length (min 1, max 500)"""
        # Too short (empty handled separately)
        response = client.post(
            "/api/search", json={"query": "", "language": "en"}
        )
        assert response.status_code == 422

        # Too long
        long_query = "a" * 501
        response = client.post(
            "/api/search", json={"query": long_query, "language": "en"}
        )
        assert response.status_code == 422

    def test_search_meilisearch_error(self):
        """Should handle Meilisearch failures gracefully"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.side_effect = Exception("Meilisearch connection failed")

            response = client.post(
                "/api/search", json={"query": "test", "language": "en"}
            )

            assert response.status_code == 503  # Service unavailable
            data = response.json()
            assert "detail" in data

    def test_search_snippet_truncation(self, mock_search_results):
        """Should truncate long content to snippet (max 200 chars)"""
        # Create result with very long content
        long_content = "x" * 1000
        mock_search_results[0].content = long_content

        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            response = client.post(
                "/api/search", json={"query": "test", "language": "en"}
            )

            assert response.status_code == 200
            snippet = response.json()["sources"][0]["snippet"]
            assert len(snippet) <= 203  # 200 chars + "..."

    def test_search_returns_top_sources(self, mock_search_results):
        """Should return sources ordered by relevance"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            response = client.post(
                "/api/search", json={"query": "test", "language": "en", "limit": 10}
            )

            assert response.status_code == 200
            sources = response.json()["sources"]

            # Check sources are ordered by relevance (descending)
            if len(sources) > 1:
                for i in range(len(sources) - 1):
                    assert sources[i]["relevance_score"] >= sources[i + 1]["relevance_score"]


class TestSearchPrivacy:
    """Test privacy requirements for /api/search"""

    def test_search_privacy_no_query_logging(self, caplog, mock_search_results):
        """Must NOT log user query (privacy!)"""
        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            sensitive_query = "my private medical condition"
            client.post(
                "/api/search", json={"query": sensitive_query, "language": "en"}
            )

            # Check logs don't contain query
            # Note: This depends on LOG_USER_QUERIES setting being False
            log_text = caplog.text.lower()
            assert "private medical condition" not in log_text

    def test_search_no_user_tracking(self):
        """Must not set tracking cookies or headers"""
        response = client.post(
            "/api/search", json={"query": "test query", "language": "en"}
        )

        # No tracking cookies
        assert "Set-Cookie" not in response.headers

        # No tracking headers
        assert "X-User-ID" not in response.headers
        assert "X-Session-ID" not in response.headers


class TestSearchPerformance:
    """Test performance requirements"""

    @pytest.mark.performance
    def test_search_response_time(self, mock_search_results):
        """Search must complete in < 200ms (fast!)"""
        import time

        with patch("search_api.main.search_client.search") as mock_search:
            mock_search.return_value = mock_search_results

            start = time.time()
            response = client.post(
                "/api/search", json={"query": "test query", "language": "en"}
            )
            duration = time.time() - start

            assert response.status_code == 200
            # Allow some overhead for HTTP, but should be very fast with mock
            assert duration < 0.5  # 500ms with HTTP overhead

    @pytest.mark.performance
    def test_search_no_llm_call(self, mock_search_results):
        """Search endpoint must NOT call LLM (that's for summarize)"""
        with patch("search_api.main.search_client.search") as mock_search:
            with patch("search_api.main.ollama_client.generate") as mock_llm:
                mock_search.return_value = mock_search_results

                client.post(
                    "/api/search", json={"query": "test", "language": "en"}
                )

                # LLM should never be called
                mock_llm.assert_not_called()
