"""Plain-text transcript normalizer — pass-through with light cleanup."""

from __future__ import annotations

from ..models import MeetingMetadata, NormalizedTranscript


def normalize_txt(raw: str, metadata: MeetingMetadata) -> NormalizedTranscript:
    # Strip blank lines + trailing whitespace; preserve everything else.
    cleaned = "\n".join(line.rstrip() for line in raw.splitlines() if line.strip())
    return NormalizedTranscript(
        text=cleaned,
        metadata=metadata,
        source_format="txt",
    )
