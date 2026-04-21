"""Example: poll Microsoft Teams for new transcripts and process them.

Complete the setup in docs/06-teams-integration.md first, then run:

    python -m meeting_agent.cli --help            # confirm CLI works
    export TEAMS_TENANT_ID=...                    # or use .env
    python examples/teams_polling.py

This runs forever. Stop with Ctrl-C. Adapt the loop to cron / systemd /
Azure WebJob / k8s CronJob for production deployments.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from meeting_agent.config import load_config
from meeting_agent.enhancer import MeetingEnhancer
from meeting_agent.renderer import build_artifact_filename, render_notes
from meeting_agent.router import build_router
from meeting_agent.sources.teams_source import TeamsTranscriptSource

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    cfg = load_config("config.yaml")
    source = TeamsTranscriptSource(cfg.teams)
    router = build_router(cfg)
    enhancer = MeetingEnhancer(router, cfg)

    # On cold start, look back 2 hours so we catch anything published during downtime
    last_seen = datetime.now(tz=timezone.utc) - timedelta(hours=2)
    logger.info("Starting Teams polling loop (interval=%ds)", cfg.teams.poll_interval_seconds)

    while True:
        try:
            new_transcripts = await source.list_new_transcripts(since=last_seen)
            if not new_transcripts:
                logger.debug("No new transcripts")
            for t in sorted(new_transcripts, key=lambda x: x.created_datetime):
                logger.info(
                    "Processing transcript meeting=%s created=%s",
                    t.meeting_id, t.created_datetime.isoformat(),
                )
                transcript = await source.fetch_transcript(t)
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
                logger.info("Wrote %s (provider=%s)", filename, notes.provider_used)
                last_seen = t.created_datetime
        except Exception:  # noqa: BLE001
            logger.exception("Poll cycle failed — will retry")

        await asyncio.sleep(cfg.teams.poll_interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
