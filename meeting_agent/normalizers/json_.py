"""JSON transcript normalizer.

Accepts either a list of utterance objects or an object with a "segments" / "utterances"
key. Each utterance is expected to have `speaker` and `text` (or similar) fields.
"""

from __future__ import annotations

import json
from typing import Any

from ..models import MeetingMetadata, NormalizedTranscript


def normalize_json(raw: str, metadata: MeetingMetadata) -> NormalizedTranscript:
    data: Any = json.loads(raw)

    utterances: list[dict[str, Any]]
    if isinstance(data, list):
        utterances = data
    elif isinstance(data, dict):
        utterances = (
            data.get("segments")
            or data.get("utterances")
            or data.get("transcript")
            or []
        )
        # Allow metadata in the JSON to override defaults when provided
        meta = data.get("metadata") or {}
        if meta.get("title"):
            metadata.title = meta["title"]
        if meta.get("date"):
            metadata.date = meta["date"]
        if meta.get("duration"):
            metadata.duration = meta["duration"]
        if meta.get("attendees"):
            metadata.attendees = list(meta["attendees"])
    else:
        utterances = []

    lines: list[str] = []
    for u in utterances:
        if not isinstance(u, dict):
            continue
        speaker = u.get("speaker") or u.get("name") or ""
        text = u.get("text") or u.get("content") or ""
        if not text:
            continue
        lines.append(f"{speaker}: {text}" if speaker else text)

    return NormalizedTranscript(
        text="\n".join(lines),
        metadata=metadata,
        source_format="json",
    )
