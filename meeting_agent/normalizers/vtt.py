"""WebVTT normalizer — strips cue IDs, timestamps, headers; keeps speaker + text."""

from __future__ import annotations

import re

from ..models import MeetingMetadata, NormalizedTranscript


def normalize_vtt(raw: str, metadata: MeetingMetadata) -> NormalizedTranscript:
    lines = raw.splitlines()
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("WEBVTT") or stripped.startswith("NOTE"):
            continue
        if "-->" in stripped:
            continue
        # VTT cue IDs are numeric or UUID-like on their own line
        if re.fullmatch(r"[0-9a-f\-]+", stripped, re.IGNORECASE):
            continue
        cleaned.append(stripped)
    return NormalizedTranscript(
        text="\n".join(cleaned),
        metadata=metadata,
        source_format="vtt",
    )
