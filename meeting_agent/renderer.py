"""Template renderer — uses Jinja2 to fill user-provided markdown templates.

Placeholders available:
  {{ meeting.title }}       — meeting title
  {{ meeting.date }}        — ISO date
  {{ meeting.duration }}    — human-readable
  {{ meeting.attendees }}   — list of strings (use `| join(', ')`)
  {{ meeting.organizer }}   — string
  {{ meeting.client }}      — optional
  {{ meeting.project }}     — optional

  {{ summary.one_liner }}
  {{ summary.topics }}      — list of {topic, bullets}

  {{ action_items }}        — list of {owner, action, due}
  {{ decisions }}           — list of {decision, decided_by}
  {{ open_questions }}      — list of strings

  {{ context.people_mentioned }}
  {{ context.organizations_mentioned }}
  {{ context.projects_mentioned }}
  {{ context.numeric_values_mentioned }}

  {{ provider_used }}       — which LLM produced this
  {{ generated_at }}        — UTC timestamp

See templates/*.md for working examples using these placeholders.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from .models import EnhancedNotes, MeetingMetadata


def render_notes(
    template_path: str | Path,
    notes: EnhancedNotes,
    metadata: MeetingMetadata,
) -> str:
    p = Path(template_path)
    env = Environment(
        loader=FileSystemLoader(str(p.parent) or "."),
        autoescape=select_autoescape(disabled_extensions=("md", "txt")),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(p.name)
    return template.render(
        meeting=metadata,
        summary=notes.summary,
        action_items=notes.action_items,
        decisions=notes.decisions,
        open_questions=notes.open_questions,
        context=notes.context,
        provider_used=notes.provider_used,
        generated_at=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )


def build_artifact_filename(metadata: MeetingMetadata) -> str:
    """Default filename pattern: [Client]_[Project]_MeetingNotes_[YYYY-MM-DD].md"""
    def sanitize(s: str) -> str:
        return (
            "".join(c if c.isalnum() else "_" for c in s).strip("_") or "Unknown"
        )

    date_part = (metadata.date or datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"))[:10]
    client = sanitize(metadata.client or "Untagged")
    project = sanitize(metadata.project or "Meeting")
    title = sanitize(metadata.title or "")[:40] if not metadata.client else ""
    suffix = f"_{title}" if title else ""
    return f"{client}_{project}{suffix}_MeetingNotes_{date_part}.md"
