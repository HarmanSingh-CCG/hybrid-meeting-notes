"""Microsoft Teams transcript source.

Polls Microsoft Graph for new meeting transcripts and returns them for
processing. Uses app-only (client credentials) auth, requires:
  - Entra ID app registration with:
      - OnlineMeetingTranscript.Read.All (Application)
      - OnlineMeetings.Read.All (Application)
      - Admin consent granted
  - Teams Application Access Policy scoping the app to specific users
    (see docs/06-teams-integration.md)

Uses the `/beta/` endpoint because `getAllTranscripts` is not available
on `/v1.0/` as of 2026.

This is a reference implementation — users can take it, adapt, or
replace with their own source. The main pipeline is agnostic about
where transcripts come from.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import aiohttp

from ..config import TeamsConfig
from ..models import MeetingMetadata, NormalizedTranscript
from ..normalizers.vtt import normalize_vtt

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_BETA = "https://graph.microsoft.com/beta"
TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"


@dataclass
class _TranscriptSummary:
    meeting_id: str
    transcript_id: str
    created_datetime: datetime


class TeamsTranscriptSource:
    def __init__(self, config: TeamsConfig):
        self._cfg = config
        self._token: str | None = None
        self._token_expires: datetime | None = None

    async def _get_token(self) -> str:
        if (
            self._token
            and self._token_expires
            and self._token_expires > datetime.now(tz=timezone.utc) + timedelta(minutes=5)
        ):
            return self._token
        url = TOKEN_URL.format(tenant=self._cfg.tenant_id)
        data = {
            "client_id": self._cfg.client_id,
            "client_secret": self._cfg.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                resp.raise_for_status()
                body = await resp.json()
        self._token = body["access_token"]
        self._token_expires = datetime.now(tz=timezone.utc) + timedelta(
            seconds=int(body.get("expires_in", 3600))
        )
        return self._token

    async def list_new_transcripts(
        self, since: datetime
    ) -> list[_TranscriptSummary]:
        """Return transcripts created after `since`. Uses /beta/ endpoint."""
        token = await self._get_token()
        # Graph rejects microseconds in query params
        since_utc = since.astimezone(timezone.utc).replace(microsecond=0)
        since_iso = since_utc.isoformat().replace("+00:00", "Z")
        user_id = self._cfg.target_user_id
        # getAllTranscripts is a Graph function with startDateTime as a
        # FUNCTION parameter (inside parens), NOT an OData $filter.
        url = (
            f"{GRAPH_BETA}/users/{user_id}/onlineMeetings/getAllTranscripts"
            f"(meetingOrganizerUserId='{user_id}',startDateTime={since_iso})"
        )

        results: list[_TranscriptSummary] = []
        async with aiohttp.ClientSession() as session:
            while url:
                async with session.get(
                    url, headers={"Authorization": f"Bearer {token}"}
                ) as resp:
                    if resp.status >= 400:
                        body_text = await resp.text()
                        logger.error("Graph error %s on %s: %s", resp.status, url, body_text[:500])
                        resp.raise_for_status()
                    body = await resp.json()

                for item in body.get("value", []):
                    meeting_id = item.get("meetingId") or _extract_meeting_id(item)
                    transcript_id = item.get("id", "")
                    created_raw = item.get("createdDateTime", "")
                    if not (meeting_id and transcript_id and created_raw):
                        continue
                    try:
                        created_dt = datetime.fromisoformat(
                            created_raw.replace("Z", "+00:00")
                        )
                    except Exception:  # noqa: BLE001
                        continue
                    results.append(
                        _TranscriptSummary(
                            meeting_id=meeting_id,
                            transcript_id=transcript_id,
                            created_datetime=created_dt,
                        )
                    )
                url = body.get("@odata.nextLink")
        return results

    async def fetch_transcript(
        self, summary: _TranscriptSummary
    ) -> NormalizedTranscript:
        """Fetch VTT content + meeting metadata and return a normalized transcript."""
        token = await self._get_token()
        user_id = self._cfg.target_user_id

        # VTT content
        vtt_url = (
            f"{GRAPH_BASE}/users/{user_id}/onlineMeetings/{summary.meeting_id}"
            f"/transcripts/{summary.transcript_id}/content?$format=text/vtt"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                vtt_url, headers={"Authorization": f"Bearer {token}"}
            ) as resp:
                resp.raise_for_status()
                vtt_raw = await resp.text()

            # Meeting metadata
            meta_url = f"{GRAPH_BASE}/users/{user_id}/onlineMeetings/{summary.meeting_id}"
            async with session.get(
                meta_url, headers={"Authorization": f"Bearer {token}"}
            ) as resp:
                resp.raise_for_status()
                meta_raw = await resp.json()

        metadata = _build_meeting_metadata(meta_raw)
        return normalize_vtt(vtt_raw, metadata)


def _build_meeting_metadata(raw: dict) -> MeetingMetadata:
    subject = raw.get("subject") or "(no subject)"
    start = raw.get("startDateTime") or ""
    end = raw.get("endDateTime") or ""
    duration = _format_duration(start, end)
    attendees: list[str] = []
    for key in ("attendees", "producers"):
        for p in (raw.get("participants") or {}).get(key, []) or []:
            identity = (p.get("identity") or {}).get("user") or {}
            name = identity.get("displayName")
            if name:
                attendees.append(name)
    return MeetingMetadata(
        title=subject, date=start or "", duration=duration, attendees=attendees
    )


def _format_duration(start: str, end: str) -> str:
    try:
        s = datetime.fromisoformat(start.replace("Z", "+00:00"))
        e = datetime.fromisoformat(end.replace("Z", "+00:00"))
        mins = int((e - s).total_seconds() // 60)
        if mins < 60:
            return f"{mins}m"
        return f"{mins // 60}h {mins % 60}m"
    except Exception:  # noqa: BLE001
        return "unknown"


def _extract_meeting_id(item: dict) -> str:
    content_url = item.get("transcriptContentUrl") or ""
    m = re.search(r"onlineMeetings/([^/]+)/transcripts/", content_url)
    return m.group(1) if m else ""
