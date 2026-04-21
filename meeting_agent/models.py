"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MeetingMetadata:
    title: str
    date: str = ""            # ISO 8601
    duration: str = ""        # human-readable, e.g. "1h 12m"
    attendees: list[str] = field(default_factory=list)
    organizer: str = ""
    client: str = ""          # optional — parsed from title or set by caller
    project: str = ""
    meeting_type: str = ""


@dataclass
class NormalizedTranscript:
    """Unified representation after stripping VTT/SRT/JSON specifics."""
    text: str                   # plain-text transcript, speaker + content
    metadata: MeetingMetadata
    source_format: str = ""     # "vtt" | "srt" | "txt" | "json" | "teams"


@dataclass
class EnhancedNotes:
    summary: dict[str, Any]
    action_items: list[dict[str, Any]]
    decisions: list[dict[str, Any]]
    open_questions: list[str]
    context: dict[str, list[str]]    # entities extracted (people, orgs, $, etc.)
    raw_llm_output: str = ""
    provider_used: str = ""          # "ollama" | "anthropic" | etc — for debugging
