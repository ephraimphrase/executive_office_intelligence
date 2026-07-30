import asyncio
import json
import logging
import os

import httpx

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.use_mock = not bool(self.api_key)
        self.client = httpx.AsyncClient(timeout=60.0)

    async def _request_with_retry(self, url: str, payload: dict, max_retries=3) -> dict:
        if self.use_mock:
            return self._get_mock_response(payload)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(max_retries):
            try:
                response = await self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        return {}

    def _get_mock_response(self, payload: dict) -> dict:
        logger.info("Using mock OpenAI response")
        if "messages" in payload:
            return {
                "choices": [{"message": {"content": "MOCK RESPONSE: Generated based on prompt."}}],
                "usage": {"total_tokens": 100}
            }
        elif "input" in payload:
            return {
                "data": [{"embedding": self._pseudo_embedding(payload.get("input", ""))}],
                "usage": {"total_tokens": 10}
            }
        return {}

    def _pseudo_embedding(self, text: str, dim: int = 3072) -> list:
        """Deterministic pseudo-embedding for mock mode: the same text always
        produces the same vector (unlike a real all-zero placeholder, this at
        least lets cosine-similarity code paths be exercised meaningfully
        without a real API key — it's not semantically aware, just non-degenerate)."""
        import hashlib
        import random

        seed = int(hashlib.sha256((text or "").encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)
        return [rng.uniform(-1, 1) for _ in range(dim)]

    async def complete(self, system_prompt: str, user_message: str, model: str = "gpt-4o", temperature: float = 0.7, max_tokens: int = 2000) -> str:
        payload = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        response = await self._request_with_retry("https://api.openai.com/v1/chat/completions", payload)
        if self.use_mock:
            return response["choices"][0]["message"]["content"]
        return response["choices"][0]["message"]["content"]

    async def embed(self, text: str) -> list[float]:
        payload = {
            "model": "text-embedding-3-large",
            "input": text
        }
        response = await self._request_with_retry("https://api.openai.com/v1/embeddings", payload)
        if self.use_mock:
            return response["data"][0]["embedding"]
        return response["data"][0]["embedding"]

    async def extract_structured(self, system_prompt: str, user_message: str, response_schema: dict) -> dict:
        payload = {
            "model": "gpt-4o",
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_extraction",
                    "schema": response_schema
                }
            }
        }
        if self.use_mock:
            logger.info("Returning empty mock structured data")
            return {}
            
        response = await self._request_with_retry("https://api.openai.com/v1/chat/completions", payload)
        content = response["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except Exception:
            return {}

_openai_client = None

def get_openai_client() -> OpenAIClient:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
