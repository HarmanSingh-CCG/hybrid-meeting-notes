"""Renderer tests — verify template variables resolve correctly."""

from meeting_agent.models import EnhancedNotes, MeetingMetadata
from meeting_agent.renderer import build_artifact_filename, render_notes


def _notes() -> EnhancedNotes:
    return EnhancedNotes(
        summary={
            "one_liner": "Team synced on Q3.",
            "topics": [{"topic": "Q3 Planning", "bullets": ["Ship X", "Hire Y"]}],
        },
        action_items=[{"owner": "Alex", "action": "Draft proposal", "due": "Friday"}],
        decisions=[{"decision": "Use NATS over Kafka", "decided_by": "Jane"}],
        open_questions=["Who owns SLAs?"],
        context={
            "people_mentioned": ["Alex", "Jane"],
            "organizations_mentioned": ["Acme"],
            "projects_mentioned": ["Platform"],
            "numeric_values_mentioned": ["$240K"],
        },
        raw_llm_output="",
        provider_used="ollama",
    )


def _meta() -> MeetingMetadata:
    return MeetingMetadata(
        title="Q3 Kickoff",
        date="2026-04-21",
        duration="45m",
        attendees=["Alex", "Jane"],
        client="Acme",
        project="Platform",
    )


def test_detailed_template_renders():
    out = render_notes("templates/detailed_notes.md", _notes(), _meta())
    assert "Q3 Kickoff" in out
    assert "Acme" in out
    assert "NATS over Kafka" in out
    assert "Draft proposal" in out


def test_executive_brief_template_renders():
    out = render_notes("templates/executive_brief.md", _notes(), _meta())
    assert "Team synced on Q3." in out
    assert "ollama" in out


def test_standup_template_renders():
    out = render_notes("templates/standup_recap.md", _notes(), _meta())
    assert "Q3 Planning" in out


def test_client_template_renders():
    out = render_notes("templates/client_meeting.md", _notes(), _meta())
    assert "Acme" in out
    assert "$240K" in out


def test_filename_follows_convention():
    name = build_artifact_filename(_meta())
    assert name.startswith("Acme_Platform_")
    assert name.endswith("_MeetingNotes_2026-04-21.md")
