# Lookuply Search API

FastAPI backend providing AI-powered search with chat interface.

## Features

- **Chat endpoint** (`/chat`) - AI-powered Q&A with source citations
- **Meilisearch integration** - Fast, relevant search results
- **Ollama integration** - LLM-powered answer generation
- **Privacy-first** - No user tracking, no query logging (configurable)
- **CORS configured** - Restrictive origins for security

## API Endpoints

### `POST /chat`

Chat with AI search assistant.

**Request:**
```json
{
  "query": "What is Python?",
  "limit": 5
}
```

**Response:**
```json
{
  "answer": "Python is a high-level programming language...",
  "sources": [
    {
      "title": "Python Guide",
      "url": "https://example.com/python",
      "snippet": "Python is..."
    }
  ],
  "query": "What is Python?"
}
```

### `GET /health`

Health check endpoint.

## Development

```bash
# Install dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run tests
pytest --cov=src

# Run locally
uvicorn search_api.main:app --reload
```

## Docker

```bash
docker build -t search-api .
docker run -p 8002:8002 \
  -e MEILISEARCH_URL=http://meilisearch:7700 \
  -e OLLAMA_URL=http://ai-evaluator:11434 \
  search-api
```

## Configuration

See `config.py` for all environment variables:

- `MEILISEARCH_URL` - Meilisearch server
- `MEILISEARCH_KEY` - API key
- `OLLAMA_URL` - Ollama server
- `OLLAMA_MODEL` - Model name
- `LOG_USER_QUERIES` - Privacy setting (default: false)

## Architecture

```
User Query → FastAPI
           ↓
    Meilisearch Search
           ↓
    Build Context
           ↓
    Ollama (LLM)
           ↓
    Answer + Sources
```

## Tests

- MeilisearchClient: 7 tests
- ChatService: 3 tests
- Total: 10+ tests with >70% coverage

## License

Part of Lookuply project.
