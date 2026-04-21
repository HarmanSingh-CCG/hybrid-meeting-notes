"""Transcript enhancement pipeline — chunks if needed, calls LLM, parses JSON."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from .config import Config
from .models import EnhancedNotes, NormalizedTranscript
from .prompts import (
    CHUNK_PROMPT_TEMPLATE,
    REDUCE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)
from .providers.base import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)

# Approximate chars-per-token ratio for English text
CHARS_PER_TOKEN = 4


def _approx_token_count(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def _chunk(text: str, token_budget: int, overlap_tokens: int) -> list[str]:
    """Split long text into overlapping chunks that fit the token budget."""
    if _approx_token_count(text) <= token_budget:
        return [text]
    chunk_chars = token_budget * CHARS_PER_TOKEN
    overlap_chars = overlap_tokens * CHARS_PER_TOKEN
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap_chars
    return chunks


def _extract_json(raw: str) -> dict[str, Any]:
    """Extract the first JSON object from LLM output, tolerating surrounding text."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in LLM output: {raw[:200]}")
    return json.loads(match.group(0))


class MeetingEnhancer:
    def __init__(self, provider: LLMProvider, config: Config):
        self._provider = provider
        self._config = config

    async def enhance(self, transcript: NormalizedTranscript) -> EnhancedNotes:
        chunks = _chunk(
            transcript.text,
            self._config.chunk_token_budget,
            self._config.chunk_overlap_tokens,
        )
        if len(chunks) == 1:
            return await self._single(chunks[0], transcript)
        return await self._map_reduce(chunks, transcript)

    async def _single(
        self, text: str, transcript: NormalizedTranscript
    ) -> EnhancedNotes:
        meta = transcript.metadata
        user_prompt = USER_PROMPT_TEMPLATE.format(
            title=meta.title,
            date=meta.date,
            duration=meta.duration,
            attendees=", ".join(meta.attendees),
            transcript=text,
        )
        response = await self._provider.chat(SYSTEM_PROMPT, user_prompt)
        parsed = _extract_json(response.content)
        return self._build(parsed, response.content, response.provider)

    async def _map_reduce(
        self, chunks: list[str], transcript: NormalizedTranscript
    ) -> EnhancedNotes:
        logger.info("Enhancing long transcript: %d chunks", len(chunks))
        chunk_outputs: list[str] = []
        prior = "(none)"
        provider_label = ""
        for i, chunk in enumerate(chunks):
            prompt = CHUNK_PROMPT_TEMPLATE.format(
                chunk_index=i + 1,
                chunk_total=len(chunks),
                prior_context=prior,
                chunk=chunk,
            )
            response = await self._provider.chat(SYSTEM_PROMPT, prompt)
            chunk_outputs.append(response.content)
            provider_label = response.provider
            try:
                parsed = _extract_json(response.content)
                prior = parsed.get("summary", {}).get("one_liner", "(none)")
            except Exception:  # noqa: BLE001
                prior = "(unavailable)"

        meta = transcript.metadata
        reduce_prompt = (
            f"Meeting: {meta.title} ({meta.date}, {meta.duration})\n"
            f"Attendees: {', '.join(meta.attendees)}\n\n"
            + REDUCE_PROMPT_TEMPLATE.format(
                chunk_count=len(chunk_outputs),
                chunk_outputs="\n---\n".join(chunk_outputs),
            )
        )
        final = await self._provider.chat(SYSTEM_PROMPT, reduce_prompt)
        parsed = _extract_json(final.content)
        return self._build(parsed, final.content, final.provider)

    @staticmethod
    def _build(parsed: dict[str, Any], raw: str, provider: str) -> EnhancedNotes:
        return EnhancedNotes(
            summary=parsed.get("summary", {}) or {},
            action_items=parsed.get("action_items", []) or [],
            decisions=parsed.get("decisions", []) or [],
            open_questions=parsed.get("open_questions", []) or [],
            context=parsed.get("context", {}) or {},
            raw_llm_output=raw,
            provider_used=provider,
        )
