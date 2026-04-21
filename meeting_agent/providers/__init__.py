"""LLM providers — adapter pattern. Every provider implements LLMProvider."""

from __future__ import annotations

from ..config import Config
from .base import LLMProvider, LLMResponse, LLMProviderError
from .ollama import OllamaProvider
from .anthropic_ import AnthropicProvider
from .openai_ import OpenAIProvider
from .azure_openai_ import AzureOpenAIProvider


def build_provider(name: str, config: Config) -> LLMProvider:
    """Factory — returns a ready-to-use provider instance.

    Raises ValueError for unknown provider names (does NOT include 'hybrid';
    the hybrid router handles that itself by composing two providers).
    """
    key = name.lower()
    if key == "ollama":
        return OllamaProvider(config.ollama, config.temperature, config.max_output_tokens)
    if key == "anthropic":
        return AnthropicProvider(config.anthropic, config.temperature, config.max_output_tokens)
    if key == "openai":
        return OpenAIProvider(config.openai, config.temperature, config.max_output_tokens)
    if key == "azure_openai":
        return AzureOpenAIProvider(
            config.azure_openai, config.temperature, config.max_output_tokens
        )
    raise ValueError(f"Unknown LLM provider: {name}")


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "LLMProviderError",
    "OllamaProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "AzureOpenAIProvider",
    "build_provider",
]
