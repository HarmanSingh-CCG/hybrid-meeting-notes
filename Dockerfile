FROM python:3.12-slim

WORKDIR /app

# Install minimal system deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY meeting_agent ./meeting_agent
COPY templates ./templates

# Default: watch /input for new transcripts and write notes to /output
VOLUME ["/input", "/output"]
ENV MEETING_AGENT_OUTPUT_DIR=/output

# Override with `docker compose run meeting-agent python -m meeting_agent.cli ...`
ENTRYPOINT ["python", "-m", "meeting_agent.cli"]
CMD ["--help"]
