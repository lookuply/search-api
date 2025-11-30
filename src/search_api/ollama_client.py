"""Ollama client for answer generation."""

import httpx


class OllamaClient:
    """Client for Ollama LLM."""

    def __init__(self, base_url: str, model: str, timeout: int = 60) -> None:
        """Initialize Ollama client."""
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = httpx.AsyncClient(timeout=timeout)

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Generate text using Ollama."""
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system

        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
