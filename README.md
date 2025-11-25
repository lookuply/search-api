# Lookuply Search API

**RESTful API for privacy-first multilingual search**

Part of the [Lookuply](https://github.com/lookuply) open-source search engine project.

---

## Overview

The Lookuply Search API provides a fast, privacy-respecting search interface supporting all 24 EU languages. Built with FastAPI, it offers hybrid search combining full-text and semantic search with optional LLM-based re-ranking.

### Key Features

- **24 EU Languages**: Query and results in any EU language
- **Hybrid Search**: BM25 + semantic embeddings + LLM re-ranking
- **RESTful API**: Clean, documented endpoints
- **API Tiers**: Free, Starter, Pro, Enterprise
- **Rate Limiting**: Redis-based rate limiting per tier
- **Privacy-First**: No tracking, no logging of queries
- **OpenAPI Docs**: Interactive API documentation

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  FastAPI    │
│  Endpoints  │
└──────┬──────┘
       │
       ├─→ OpenSearch (full-text)
       ├─→ Qdrant (semantic)
       ├─→ Ollama (re-ranking)
       └─→ Redis (rate limiting)
```

---

## Technology Stack

- **Python 3.11+**
- **FastAPI**: Modern async web framework
- **OpenSearch**: Full-text search
- **Qdrant**: Vector search
- **Ollama**: Local LLM inference (Mistral 7B)
- **Redis**: Caching and rate limiting
- **PostgreSQL**: User and usage tracking
- **Pydantic**: Data validation

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/lookuply/search-api.git
cd search-api

# Install dependencies
pip install -r requirements.txt

# Configure API
cp .env.example .env
# Edit .env with your settings
```

### Running Locally

```bash
# Start dependencies
docker-compose up -d

# Run API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API available at: http://localhost:8000
# Docs available at: http://localhost:8000/docs
```

---

## API Endpoints

### Search

```bash
GET /api/v1/search?q=query&lang=en&page=1&limit=10

Response:
{
  "results": [
    {
      "url": "https://example.com",
      "title": "Example Page",
      "snippet": "Relevant content...",
      "score": 0.95,
      "language": "en"
    }
  ],
  "total": 1250,
  "page": 1,
  "took_ms": 45
}
```

### Autocomplete

```bash
GET /api/v1/autocomplete?q=pri&lang=en

Response:
{
  "suggestions": [
    "privacy",
    "private search",
    "privacy policy"
  ]
}
```

### Language Detection

```bash
POST /api/v1/detect-language
{
  "text": "Bonjour, comment allez-vous?"
}

Response:
{
  "language": "fr",
  "confidence": 0.98
}
```

---

## Pricing Tiers

| Tier | Searches/Month | Rate Limit | Price |
|------|----------------|------------|-------|
| **Free** | 1,000 | 10/min | €0 |
| **Starter** | 50,000 | 100/min | €29/mo |
| **Pro** | 500,000 | 500/min | €199/mo |
| **Enterprise** | Unlimited | Custom | Contact |

---

## Authentication

### API Keys

```bash
# Request with API key
curl -H "X-API-Key: your_api_key" \
  https://api.lookuply.info/api/v1/search?q=privacy

# Or via query parameter
curl https://api.lookuply.info/api/v1/search?q=privacy&api_key=your_api_key
```

### Getting an API Key

1. Sign up at [lookuply.info](https://lookuply.info)
2. Navigate to API section
3. Generate API key
4. Start searching!

---

## Search Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `q` | string | Search query (required) | - |
| `lang` | string | Language code (en, de, fr, etc.) | auto-detect |
| `page` | integer | Page number | 1 |
| `limit` | integer | Results per page (max 100) | 10 |
| `safe` | boolean | Safe search filter | false |
| `rerank` | boolean | Enable LLM re-ranking | false |

---

## Configuration

Environment variables in `.env`:

```bash
# API Settings
API_TITLE=Lookuply Search API
API_VERSION=1.0.0
API_HOST=0.0.0.0
API_PORT=8000

# OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/lookuply

# Ollama (LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:7b

# Rate Limiting
RATE_LIMIT_FREE=10/minute
RATE_LIMIT_STARTER=100/minute
RATE_LIMIT_PRO=500/minute
```

---

## Development

### Project Structure

```
search-api/
├── app/
│   ├── api/             # API endpoints
│   │   └── v1/
│   │       ├── search.py
│   │       ├── autocomplete.py
│   │       └── auth.py
│   ├── core/            # Core functionality
│   │   ├── search.py    # Search logic
│   │   ├── ranking.py   # Ranking algorithms
│   │   └── config.py    # Configuration
│   ├── models/          # Data models
│   ├── db/              # Database
│   └── main.py          # Application entry
├── tests/               # Tests
└── docker/              # Docker configs
```

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Load tests
locust -f tests/load/locustfile.py
```

### Code Quality

```bash
# Format
black app/

# Lint
ruff app/

# Type checking
mypy app/
```

---

## Performance

### Benchmarks

- **Average response time**: 45ms (without LLM)
- **P95 response time**: 120ms
- **P99 response time**: 250ms
- **With LLM re-ranking**: +150ms average

### Scaling

- Horizontal scaling via multiple instances
- Redis for shared rate limiting
- PostgreSQL read replicas for analytics

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/lookuply/.github/blob/main/CONTRIBUTING.md).

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

## Related Projects

- [lookuply/crawler](https://github.com/lookuply/crawler) - Web crawler
- [lookuply/indexer](https://github.com/lookuply/indexer) - Content indexing
- [lookuply/frontend](https://github.com/lookuply/frontend) - Web interface

---

## Links

- **Website**: [lookuply.info](https://lookuply.info)
- **API**: [api.lookuply.info](https://api.lookuply.info)
- **Documentation**: [docs.lookuply.info](https://docs.lookuply.info)
- **Status**: [status.lookuply.info](https://status.lookuply.info)

---

**Privacy-first search API. 24 languages. Open source.**
