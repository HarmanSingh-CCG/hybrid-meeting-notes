"""Ollama provider — local inference. Supports any model Ollama can serve
(Gemma, Llama, Mistral, Qwen, Phi, etc.)."""

from __future__ import annotations

import asyncio
import logging

import aiohttp

from ..config import OllamaConfig
from .base import LLMProvider, LLMProviderError, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, config: OllamaConfig, temperature: float, max_output_tokens: int):
        self._config = config
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._timeout = aiohttp.ClientTimeout(total=config.timeout_seconds)

    async def chat(self, system: str, user: str) -> LLMResponse:
        url = f"{self._config.endpoint.rstrip('/')}/api/chat"
        headers = {"Content-Type": "application/json"}
        if self._config.api_key:
            # For Caddy-proxied Ollama with API key auth
            headers["X-API-Key"] = self._config.api_key

        payload = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {
                "temperature": self._temperature,
                "num_predict": self._max_output_tokens,
            },
        }

        last_err: Exception | None = None
        for attempt in range(3):
            try:
                start = asyncio.get_event_loop().time()
                async with aiohttp.ClientSession(timeout=self._timeout) as session:
                    async with session.post(url, json=payload, headers=headers) as resp:
                        if resp.status != 200:
                            body = await resp.text()
                            raise RuntimeError(f"Ollama {resp.status}: {body[:200]}")
                        data = await resp.json()
                elapsed = asyncio.get_event_loop().time() - start
                return LLMResponse(
                    content=(data.get("message") or {}).get("content", ""),
                    provider=self.name,
                    model=self._config.model,
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    latency_seconds=elapsed,
                )
            except Exception as err:  # noqa: BLE001
                last_err = err
                logger.warning("Ollama attempt %d/3 failed: %s", attempt + 1, err)
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)

        raise LLMProviderError(f"Ollama failed after 3 attempts. Last error: {last_err}")
