"""Base LLMProvider interface. Every provider returns the same shape."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    provider: str              # "ollama" | "anthropic" | etc.
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_seconds: float = 0.0


class LLMProviderError(RuntimeError):
    """Raised when a provider fails after its own internal retries."""


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def chat(self, system: str, user: str) -> LLMResponse:
        """Single-turn chat call. Provider handles its own retries."""
