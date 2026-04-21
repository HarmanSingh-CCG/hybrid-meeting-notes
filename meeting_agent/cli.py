"""Command-line interface for hybrid-meeting-notes.

Usage:
  meeting-agent process <transcript-file> [--title "..."] [--client "..."] ...
  meeting-agent process-stdin [--title "..."]
  meeting-agent --config path/to/config.yaml process ...

Writes enhanced notes (markdown) and a structured JSON companion to
the configured output directory.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
from pathlib import Path

import click

from .config import Config, load_config
from .enhancer import MeetingEnhancer
from .models import EnhancedNotes, MeetingMetadata, NormalizedTranscript
from .renderer import build_artifact_filename, render_notes
from .router import build_router
from .sources.file_source import load_from_file
from .normalizers.txt import normalize_txt


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _extract_client_project(title: str, regex: str) -> tuple[str, str]:
    try:
        match = re.search(regex, title)
    except re.error:
        return "", ""
    if not match:
        return "", ""
    groups = match.groups()
    client = groups[0] if len(groups) >= 1 else ""
    project = groups[1] if len(groups) >= 2 else ""
    return client, project


async def _run_pipeline(
    cfg: Config, transcript: NormalizedTranscript
) -> tuple[str, EnhancedNotes, str]:
    # Attempt to auto-populate client/project from title if not already set
    if not transcript.metadata.client and not transcript.metadata.project:
        c, p = _extract_client_project(
            transcript.metadata.title, cfg.metadata.title_regex
        )
        transcript.metadata.client = c
        transcript.metadata.project = p

    router = build_router(cfg)
    enhancer = MeetingEnhancer(router, cfg)
    notes = await enhancer.enhance(transcript)

    markdown = render_notes(cfg.template, notes, transcript.metadata)
    filename = build_artifact_filename(transcript.metadata)
    return filename, notes, markdown


def _write_outputs(
    cfg: Config, filename: str, notes: EnhancedNotes, markdown: str
) -> tuple[Path, Path]:
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / filename
    json_path = md_path.with_suffix(".json")
    md_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "summary": notes.summary,
                "action_items": notes.action_items,
                "decisions": notes.decisions,
                "open_questions": notes.open_questions,
                "context": notes.context,
                "provider_used": notes.provider_used,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return md_path, json_path


@click.group()
@click.option(
    "--config",
    "config_path",
    type=click.Path(dir_okay=False),
    default=None,
    help="Path to config.yaml (optional — env vars also honored).",
)
@click.option("--verbose", "-v", is_flag=True, help="Debug logging.")
@click.pass_context
def cli(ctx: click.Context, config_path: str | None, verbose: bool) -> None:
    _configure_logging(verbose)
    ctx.obj = load_config(config_path)


@cli.command("process")
@click.argument("transcript_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--title", default=None, help="Meeting title.")
@click.option("--date", default=None, help="Meeting date (ISO 8601).")
@click.option("--duration", default=None, help="Human-readable duration.")
@click.option("--attendees", default=None, help="Comma-separated attendees.")
@click.option("--client", default="", help="Optional client name.")
@click.option("--project", default="", help="Optional project name.")
@click.pass_context
def process_cmd(
    ctx: click.Context,
    transcript_path: str,
    title: str | None,
    date: str | None,
    duration: str | None,
    attendees: str | None,
    client: str,
    project: str,
) -> None:
    """Process a single transcript file and write enhanced notes to disk."""
    cfg: Config = ctx.obj
    attendee_list = [a.strip() for a in (attendees or "").split(",") if a.strip()]
    transcript = load_from_file(
        transcript_path,
        title=title,
        date=date,
        duration=duration,
        attendees=attendee_list,
        client=client,
        project=project,
    )

    filename, notes, markdown = asyncio.run(_run_pipeline(cfg, transcript))
    md_path, json_path = _write_outputs(cfg, filename, notes, markdown)
    click.echo(f"Wrote {md_path}")
    click.echo(f"Wrote {json_path}")
    click.echo(f"Provider used: {notes.provider_used}")


@cli.command("process-stdin")
@click.option("--title", default="Pasted Meeting", help="Meeting title.")
@click.option("--date", default=None, help="Meeting date (ISO 8601).")
@click.option("--duration", default=None, help="Human-readable duration.")
@click.option("--attendees", default=None, help="Comma-separated attendees.")
@click.option("--client", default="", help="Optional client name.")
@click.option("--project", default="", help="Optional project name.")
@click.pass_context
def process_stdin_cmd(
    ctx: click.Context,
    title: str,
    date: str | None,
    duration: str | None,
    attendees: str | None,
    client: str,
    project: str,
) -> None:
    """Process transcript from stdin (paste + Ctrl-D on macOS/Linux)."""
    cfg: Config = ctx.obj
    raw = sys.stdin.read()
    if not raw.strip():
        click.echo("No input on stdin.", err=True)
        sys.exit(1)
    attendee_list = [a.strip() for a in (attendees or "").split(",") if a.strip()]
    metadata = MeetingMetadata(
        title=title,
        date=date or "",
        duration=duration or "",
        attendees=attendee_list,
        client=client,
        project=project,
    )
    transcript = normalize_txt(raw, metadata)
    filename, notes, markdown = asyncio.run(_run_pipeline(cfg, transcript))
    md_path, json_path = _write_outputs(cfg, filename, notes, markdown)
    click.echo(f"Wrote {md_path}")
    click.echo(f"Wrote {json_path}")


def main() -> None:
    cli(obj=None)


if __name__ == "__main__":
    main()
