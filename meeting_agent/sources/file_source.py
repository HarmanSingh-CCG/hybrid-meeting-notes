"""File source — simplest onramp. Drop a transcript file on disk.

Supports: .vtt .srt .txt .json (auto-detected by extension).
"""

from __future__ import annotations

from pathlib import Path

from ..models import MeetingMetadata, NormalizedTranscript
from ..normalizers import normalize_from_file


def load_from_file(
    path: str | Path,
    title: str | None = None,
    date: str | None = None,
    duration: str | None = None,
    attendees: list[str] | None = None,
    client: str = "",
    project: str = "",
) -> NormalizedTranscript:
    """Load and normalize a transcript file. Metadata defaults to filename-derived values."""
    p = Path(path)
    meta = MeetingMetadata(
        title=title or p.stem,
        date=date or "",
        duration=duration or "",
        attendees=attendees or [],
        client=client,
        project=project,
    )
    return normalize_from_file(p, meta)
