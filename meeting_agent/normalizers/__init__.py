"""Transcript normalizers — convert various input formats into a unified plain-text form."""

from __future__ import annotations

from pathlib import Path

from ..models import MeetingMetadata, NormalizedTranscript
from .vtt import normalize_vtt
from .srt import normalize_srt
from .txt import normalize_txt
from .json_ import normalize_json


def normalize_from_file(
    path: str | Path, metadata: MeetingMetadata | None = None
) -> NormalizedTranscript:
    """Auto-detect format from file extension and normalize."""
    p = Path(path)
    suffix = p.suffix.lower()
    raw = p.read_text(encoding="utf-8")
    meta = metadata or MeetingMetadata(title=p.stem)

    if suffix == ".vtt":
        return normalize_vtt(raw, meta)
    if suffix == ".srt":
        return normalize_srt(raw, meta)
    if suffix == ".json":
        return normalize_json(raw, meta)
    # Default to plain text
    return normalize_txt(raw, meta)


__all__ = [
    "normalize_from_file",
    "normalize_vtt",
    "normalize_srt",
    "normalize_txt",
    "normalize_json",
]
