#!/usr/bin/env bash
# hybrid-meeting-notes — one-command setup.
# Creates a virtualenv, installs dependencies, copies .env.example.
# Does NOT install Ollama or pull any models — see docs/02-setup-ollama.md for that.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python 3 not found. Install Python 3.11+ and re-run."
  exit 1
fi

PY_MAJOR=$("$PY" -c 'import sys; print(sys.version_info[0])')
PY_MINOR=$("$PY" -c 'import sys; print(sys.version_info[1])')
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
  echo "Python 3.11+ required. Detected $PY_MAJOR.$PY_MINOR."
  exit 1
fi

echo "[1/3] Creating virtualenv at .venv ..."
if [ ! -d .venv ]; then
  "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/3] Installing Python dependencies ..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "[3/3] Preparing .env ..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "      Created .env from .env.example — edit it to pick a provider."
else
  echo "      .env already exists, skipped."
fi

mkdir -p output raw_transcripts

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Edit .env — pick LLM_PROVIDER (ollama | anthropic | openai | azure_openai | hybrid)"
echo "  2. (If using Ollama) see docs/02-setup-ollama.md to install Ollama and pull a model"
echo "  3. Try it out:"
echo "       source .venv/bin/activate"
echo "       python -m meeting_agent.cli process examples/sample_transcripts/standup.vtt"
echo ""
