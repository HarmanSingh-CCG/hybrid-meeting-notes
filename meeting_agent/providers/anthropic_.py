"""Anthropic provider — Claude via official SDK."""

from __future__ import annotations

import asyncio
import logging

from ..config import AnthropicConfig
from .base import LLMProvider, LLMProviderError, LLMResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, config: AnthropicConfig, temperature: float, max_output_tokens: int):
        self._config = config
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    async def chat(self, system: str, user: str) -> LLMResponse:
        if not self._config.api_key:
            raise LLMProviderError("ANTHROPIC_API_KEY not set")

        try:
            from anthropic import AsyncAnthropic
        except ImportError as err:
            raise LLMProviderError(
                "anthropic package not installed — run: pip install anthropic"
            ) from err

        client = AsyncAnthropic(api_key=self._config.api_key)

        start = asyncio.get_event_loop().time()
        try:
            msg = await client.messages.create(
                model=self._config.model,
                max_tokens=self._config.max_tokens,
                temperature=self._temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as err:  # noqa: BLE001
            raise LLMProviderError(f"Anthropic call failed: {err}") from err
        elapsed = asyncio.get_event_loop().time() - start

        content = ""
        if msg.content and hasattr(msg.content[0], "text"):
            content = msg.content[0].text

        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._config.model,
            prompt_tokens=getattr(msg.usage, "input_tokens", 0),
            completion_tokens=getattr(msg.usage, "output_tokens", 0),
            latency_seconds=elapsed,
        )
