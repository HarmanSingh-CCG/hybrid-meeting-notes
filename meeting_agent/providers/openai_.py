"""OpenAI provider."""

from __future__ import annotations

import asyncio
import logging

from ..config import OpenAIConfig
from .base import LLMProvider, LLMProviderError, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, config: OpenAIConfig, temperature: float, max_output_tokens: int):
        self._config = config
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    async def chat(self, system: str, user: str) -> LLMResponse:
        if not self._config.api_key:
            raise LLMProviderError("OPENAI_API_KEY not set")

        try:
            from openai import AsyncOpenAI
        except ImportError as err:
            raise LLMProviderError(
                "openai package not installed — run: pip install openai"
            ) from err

        client = AsyncOpenAI(api_key=self._config.api_key)

        start = asyncio.get_event_loop().time()
        try:
            resp = await client.chat.completions.create(
                model=self._config.model,
                temperature=self._temperature,
                max_tokens=self._max_output_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as err:  # noqa: BLE001
            raise LLMProviderError(f"OpenAI call failed: {err}") from err
        elapsed = asyncio.get_event_loop().time() - start

        content = resp.choices[0].message.content or "" if resp.choices else ""
        usage = resp.usage
        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._config.model,
            prompt_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            latency_seconds=elapsed,
        )
