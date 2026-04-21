# 06 — Microsoft Teams Integration

Automatically pull transcripts from Microsoft Teams meetings via Microsoft Graph. This guide was hard-won — several steps aren't documented prominently by Microsoft.

## What You Get

- Polls Graph every N minutes for new transcripts
- Fetches meeting metadata (subject, attendees, duration)
- Hands the normalized transcript to the enhancement pipeline

## Prerequisites

- Microsoft 365 tenant with Teams
- Tenant Global Administrator or Cloud Application Administrator rights
- Teams Administrator rights (for the App Access Policy step)

## Step 1 — Create an Entra ID App Registration

1. [Azure Portal](https://portal.azure.com) → **Entra ID** → **App registrations** → **+ New registration**
2. Name: `meeting-notes-agent`
3. Account type: **Single tenant**
4. Redirect URI: leave blank (client-credentials flow)
5. Click **Register**

Copy and save:
- Application (client) ID → `TEAMS_CLIENT_ID`
- Directory (tenant) ID → `TEAMS_TENANT_ID`

## Step 2 — Create a Client Secret

- In your app registration → **Certificates & secrets** → **+ New client secret**
- Copy the **Value** (not the Secret ID) immediately → `TEAMS_CLIENT_SECRET`

## Step 3 — Grant Graph API Permissions

- App registration → **API permissions** → **+ Add a permission** → **Microsoft Graph** → **Application permissions**
- Add:
  - `OnlineMeetingTranscript.Read.All`
  - `OnlineMeetings.Read.All`
- Click **Grant admin consent for <tenant>**

Both rows should flip to green ✓.

## Step 4 — Teams Application Access Policy (Critical)

This is the step Microsoft documentation underemphasizes. **Without it, every Graph call returns 403**, regardless of the API permissions above.

Run in PowerShell 7 as a Teams Admin:

```powershell
Install-Module -Name MicrosoftTeams -Scope CurrentUser -Force
Connect-MicrosoftTeams

New-CsApplicationAccessPolicy `
  -Identity "MeetingNotesAgent-ScopedAccess" `
  -AppIds @("<your-client-id>") `
  -Description "Meeting notes agent — scoped to specific users."

Grant-CsApplicationAccessPolicy `
  -PolicyName "MeetingNotesAgent-ScopedAccess" `
  -Identity "user@yourtenant.com"
```

Propagation takes up to 30 minutes. Graph calls before that return 403 or empty.

## Step 5 — Find the Target User's Entra Object ID

Azure Portal → **Users** → click the user → **Object ID**. Save as `TEAMS_TARGET_USER_ID`.

## Step 6 — Configure

```bash
# .env
TEAMS_TENANT_ID=<from-step-1>
TEAMS_CLIENT_ID=<from-step-1>
TEAMS_CLIENT_SECRET=<from-step-2>
TEAMS_TARGET_USER_ID=<from-step-5>
TEAMS_POLL_INTERVAL_SECONDS=300
```

Install the Teams transcript source (optional aiohttp-only — no additional deps beyond core):
```bash
pip install aiohttp
```

## Step 7 — Run

The `TeamsTranscriptSource` class in `meeting_agent/sources/teams_source.py` is a reference implementation. See `examples/teams_polling.py` for a polling loop that:
1. Tracks last-seen transcript timestamp
2. Polls Graph every N minutes
3. For each new transcript, runs the enhancement pipeline
4. Writes notes to the output directory

Adapt it to your deployment model (cron, systemd, Azure WebJob, AWS Lambda, Kubernetes CronJob, etc.).

## Critical Graph API Notes

These cost me multiple deploy cycles to figure out. Save yourself the pain:

1. **`getAllTranscripts` is on `/beta/`, not `/v1.0/`.** As of 2026-04, the function does not exist on v1.0 and returns 400 if you try.
2. **`startDateTime` is a FUNCTION parameter, not an OData `$filter`.** It goes inside the parens:
   ```
   /beta/users/{id}/onlineMeetings/getAllTranscripts(meetingOrganizerUserId='{id}',startDateTime=2026-04-20T22:00:00Z)
   ```
   NOT:
   ```
   /beta/users/{id}/onlineMeetings/getAllTranscripts(meetingOrganizerUserId='{id}')?$filter=createdDateTime gt 2026-04-20T22:00:00Z
   ```
3. **Timestamps must NOT include microseconds.** Python's `datetime.isoformat()` adds them. Strip with `.replace(microsecond=0)`.
4. **Distinguish 400 (path exists, malformed request) from 404 (path wrong).** Iterate on query params for 400; iterate on URL for 404.
5. **Always log the response body on Graph 4xx/5xx.** The `error.message` tells you exactly what's wrong. `aiohttp.raise_for_status()` throws before reading the body — read it first, log it, then raise.

## Why Polling and Not Subscriptions

Microsoft Graph supports real-time change-notification subscriptions on meeting transcripts. We chose polling anyway because **transcript subscriptions require resource-data encryption** — an RSA keypair + public cert + decryption layer on every notification. That's ~150 LOC of crypto infrastructure for a 5-minute-latency saving in a post-meeting workflow.

If you need sub-minute latency, swap `TeamsTranscriptSource` for a subscription-based source. The rest of the pipeline doesn't care.
