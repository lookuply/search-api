"""Configuration for Search API."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Search API settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8002

    # Meilisearch
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_key: str = ""
    meilisearch_index: str = "pages"

    # Ollama (for answer generation)
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b-instruct-q4_K_M"
    ollama_timeout: int = 60

    # Privacy settings (no user tracking)
    log_user_queries: bool = False
    enable_analytics: bool = False

    # Search settings
    max_search_results: int = 10
    min_relevance_score: float = 0.6


settings = Settings()
