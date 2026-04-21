# 07 — Self-Hosting via Docker

For users who want a reproducible, zero-dependency install.

## Quick Start

```bash
cp .env.example .env
# edit .env — set LLM_PROVIDER and credentials
docker compose up --build
```

This brings up:
- **meeting-agent** — the Python service. Watches `./input/` for new transcript files and writes notes to `./output/`.
- **ollama** (optional) — local inference server. Only included if you set `LLM_PROVIDER=ollama` in `.env`.

## File-Drop Mode

The Docker setup is configured for file-drop: save a `.vtt`, `.srt`, `.txt`, or `.json` into `./input/`, a few seconds later a notes file appears in `./output/`.

Implement your own watcher in `examples/watch_input.py` — simple inotify/polling loop.

## CLI-Only Mode

If you prefer to run the CLI ad-hoc inside the container:

```bash
docker compose run --rm meeting-agent \
  python -m meeting_agent.cli process /input/standup.vtt
```

## Using Your Host's Ollama Instead of the Docker One

If you already have Ollama running on the host:

```yaml
# docker-compose.override.yml
services:
  meeting-agent:
    environment:
      OLLAMA_ENDPOINT: http://host.docker.internal:11434
  ollama:
    # prevent the bundled Ollama from starting
    profiles: ["disabled"]
```

## Image Size

The default image is ~150 MB (Python slim + dependencies). The Ollama image is separate (~1 GB base, plus models you pull).

## Production Considerations

The Docker setup is for local / self-hosted use. For multi-tenant production:
- Replace the file-drop pattern with a proper queue (Redis, SQS, Azure Service Bus)
- Put the enhancement service behind an auth layer
- Persist output to durable storage (S3, Azure Blob, GCS) not a local volume
- Add a separate worker pool if processing concurrent meetings
