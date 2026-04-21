"""Example: process a single transcript file programmatically (no CLI).

Useful for integrating hybrid-meeting-notes into a larger Python application.
"""

import asyncio
import json
from pathlib import Path

from meeting_agent.config import load_config
from meeting_agent.enhancer import MeetingEnhancer
from meeting_agent.renderer import build_artifact_filename, render_notes
from meeting_agent.router import build_router
from meeting_agent.sources.file_source import load_from_file


async def main() -> None:
    cfg = load_config("config.yaml")  # or None to use .env only

    transcript = load_from_file(
        "examples/sample_transcripts/standup.vtt",
        title="Team Standup",
        date="2026-04-21",
        duration="8m",
        attendees=["Alex", "Priya", "Sam"],
    )

    router = build_router(cfg)
    enhancer = MeetingEnhancer(router, cfg)
    notes = await enhancer.enhance(transcript)

    markdown = render_notes(cfg.template, notes, transcript.metadata)
    filename = build_artifact_filename(transcript.metadata)

    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / filename).write_text(markdown)
    (out_dir / filename).with_suffix(".json").write_text(
        json.dumps({
            "summary": notes.summary,
            "action_items": notes.action_items,
            "decisions": notes.decisions,
            "open_questions": notes.open_questions,
            "context": notes.context,
            "provider_used": notes.provider_used,
        }, indent=2)
    )
    print(f"Wrote {out_dir / filename}")
    print(f"Provider used: {notes.provider_used}")


if __name__ == "__main__":
    asyncio.run(main())
