"""SubRip (.srt) normalizer."""

from __future__ import annotations

import re

from ..models import MeetingMetadata, NormalizedTranscript


def normalize_srt(raw: str, metadata: MeetingMetadata) -> NormalizedTranscript:
    lines = raw.splitlines()
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if "-->" in stripped:
            continue
        # SRT cue numbers are bare integers on their own line
        if re.fullmatch(r"\d+", stripped):
            continue
        cleaned.append(stripped)
    return NormalizedTranscript(
        text="\n".join(cleaned),
        metadata=metadata,
        source_format="srt",
    )
