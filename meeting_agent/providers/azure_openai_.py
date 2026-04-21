"""Azure OpenAI provider."""

from __future__ import annotations

import asyncio
import logging

from ..config import AzureOpenAIConfig
from .base import LLMProvider, LLMProviderError, LLMResponse

logger = logging.getLogger(__name__)


class AzureOpenAIProvider(LLMProvider):
    name = "azure_openai"

    def __init__(
        self, config: AzureOpenAIConfig, temperature: float, max_output_tokens: int
    ):
        self._config = config
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    async def chat(self, system: str, user: str) -> LLMResponse:
        if not self._config.api_key or not self._config.endpoint:
            raise LLMProviderError(
                "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set"
            )

        try:
            from openai import AsyncAzureOpenAI
        except ImportError as err:
            raise LLMProviderError(
                "openai package not installed — run: pip install openai"
            ) from err

        client = AsyncAzureOpenAI(
            api_key=self._config.api_key,
            azure_endpoint=self._config.endpoint,
            api_version=self._config.api_version,
        )

        start = asyncio.get_event_loop().time()
        try:
            resp = await client.chat.completions.create(
                model=self._config.deployment,  # Azure uses deployment name
                temperature=self._temperature,
                max_tokens=self._max_output_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as err:  # noqa: BLE001
            raise LLMProviderError(f"Azure OpenAI call failed: {err}") from err
        elapsed = asyncio.get_event_loop().time() - start

        content = resp.choices[0].message.content or "" if resp.choices else ""
        usage = resp.usage
        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._config.deployment,
            prompt_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            latency_seconds=elapsed,
        )
