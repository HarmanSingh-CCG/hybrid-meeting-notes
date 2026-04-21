"""Hybrid router — composes two providers with failover logic.

Design goals:
- Simple: just "local-first" or "cloud-first" with a timeout.
- Honest: log which provider actually served each request.
- Safe: never silently succeed on the wrong provider — the LLMResponse records it.
"""

from __future__ import annotations

import asyncio
import logging

from .config import Config
from .providers import build_provider
from .providers.base import LLMProvider, LLMProviderError, LLMResponse

logger = logging.getLogger(__name__)


class HybridRouter(LLMProvider):
    """Drop-in replacement for a single provider. Routes with failover."""

    name = "hybrid"

    def __init__(self, config: Config):
        self._config = config
        self._strategy = config.hybrid.strategy
        self._local = build_provider(config.hybrid.local_provider, config)
        self._cloud = build_provider(config.hybrid.cloud_provider, config)
        self._local_timeout = config.hybrid.local_timeout_seconds

    async def chat(self, system: str, user: str) -> LLMResponse:
        if self._strategy == "cloud-first":
            primary, secondary = self._cloud, self._local
            primary_label, secondary_label = "cloud", "local"
        else:
            # local-first (default)
            primary, secondary = self._local, self._cloud
            primary_label, secondary_label = "local", "cloud"

        # Try primary with a timeout
        try:
            if primary_label == "local":
                result = await asyncio.wait_for(
                    primary.chat(system, user), timeout=self._local_timeout
                )
            else:
                result = await primary.chat(system, user)
            logger.info("Hybrid: %s provider (%s) succeeded", primary_label, result.provider)
            return result
        except (asyncio.TimeoutError, LLMProviderError, Exception) as err:
            logger.warning(
                "Hybrid: %s provider failed (%s) — falling back to %s",
                primary_label,
                err,
                secondary_label,
            )

        # Fall back to secondary
        try:
            result = await secondary.chat(system, user)
            logger.info("Hybrid: %s fallback (%s) succeeded", secondary_label, result.provider)
            # Tag the response so caller knows it fell back
            result = LLMResponse(
                content=result.content,
                provider=f"{result.provider} (fallback)",
                model=result.model,
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                latency_seconds=result.latency_seconds,
            )
            return result
        except Exception as err:  # noqa: BLE001
            raise LLMProviderError(
                f"Hybrid routing failed — both {primary_label} and "
                f"{secondary_label} providers exhausted. Last error: {err}"
            ) from err


def build_router(config: Config) -> LLMProvider:
    """Return either a single provider or a hybrid router based on config.provider."""
    if config.provider == "hybrid":
        return HybridRouter(config)
    return build_provider(config.provider, config)
