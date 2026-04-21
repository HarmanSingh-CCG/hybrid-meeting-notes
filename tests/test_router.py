"""Hybrid router tests — use stub providers so nothing hits real LLM APIs."""

import asyncio

import pytest

from meeting_agent.config import Config
from meeting_agent.providers.base import LLMProvider, LLMProviderError, LLMResponse
from meeting_agent.router import HybridRouter


class _StubProvider(LLMProvider):
    def __init__(self, name: str, should_fail: bool = False, delay: float = 0.0):
        self.name = name
        self._should_fail = should_fail
        self._delay = delay

    async def chat(self, system: str, user: str) -> LLMResponse:
        await asyncio.sleep(self._delay)
        if self._should_fail:
            raise LLMProviderError(f"{self.name} failed (stub)")
        return LLMResponse(
            content='{"ok": true}',
            provider=self.name,
            model="stub",
            prompt_tokens=1,
            completion_tokens=1,
            latency_seconds=self._delay,
        )


def _make_router(local: _StubProvider, cloud: _StubProvider, strategy: str = "local-first", timeout: int = 5) -> HybridRouter:
    cfg = Config()
    cfg.hybrid.strategy = strategy
    cfg.hybrid.local_timeout_seconds = timeout
    r = HybridRouter.__new__(HybridRouter)
    r._config = cfg
    r._strategy = strategy
    r._local = local
    r._cloud = cloud
    r._local_timeout = timeout
    return r


@pytest.mark.asyncio
async def test_local_first_local_succeeds():
    r = _make_router(_StubProvider("ollama"), _StubProvider("anthropic"))
    resp = await r.chat("s", "u")
    assert resp.provider == "ollama"


@pytest.mark.asyncio
async def test_local_first_fails_over_to_cloud():
    r = _make_router(_StubProvider("ollama", should_fail=True), _StubProvider("anthropic"))
    resp = await r.chat("s", "u")
    assert "fallback" in resp.provider
    assert "anthropic" in resp.provider


@pytest.mark.asyncio
async def test_cloud_first_cloud_succeeds():
    r = _make_router(_StubProvider("ollama"), _StubProvider("anthropic"), strategy="cloud-first")
    resp = await r.chat("s", "u")
    assert resp.provider == "anthropic"


@pytest.mark.asyncio
async def test_cloud_first_fails_over_to_local():
    r = _make_router(_StubProvider("ollama"), _StubProvider("anthropic", should_fail=True), strategy="cloud-first")
    resp = await r.chat("s", "u")
    assert "fallback" in resp.provider
    assert "ollama" in resp.provider


@pytest.mark.asyncio
async def test_both_fail_raises():
    r = _make_router(
        _StubProvider("ollama", should_fail=True),
        _StubProvider("anthropic", should_fail=True),
    )
    with pytest.raises(LLMProviderError):
        await r.chat("s", "u")
