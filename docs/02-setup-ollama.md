# 02 — Setting Up Ollama (Local LLM)

This guide gets you from zero to a local LLM serving meeting notes on a Mac. For other platforms (Linux, Windows with WSL2), the Ollama docs apply — the config in this repo is platform-agnostic.

## Install Ollama

macOS (Homebrew):
```bash
brew install ollama
```

Linux / WSL2:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or download installers from [ollama.com](https://ollama.com).

## Pick a Model

Rules of thumb for the transcript summarization task:

| Model | Size | RAM Needed | Tok/sec (M-series) | Quality |
|---|---|---|---|---|
| `gemma3:1b` | ~1 GB | 8 GB | 150+ | Fast but shallow — toy/tests |
| `llama3.2:3b` | ~2 GB | 16 GB | 100+ | Good for standup recaps |
| `gemma3:12b` | ~8 GB | 24 GB | 50-60 | Solid middle ground |
| `gemma3:27b` | ~17 GB | 48 GB | 40-50 | **Recommended default** |
| `qwen2.5:72b` | ~40 GB | 96 GB | 5-10 | Best quality, slow on consumer |

Pull your chosen model:
```bash
ollama pull gemma3:27b
```

## Optional: Custom Modelfile

For meeting notes specifically, a lower temperature and larger context window help. Create `Modelfile`:

```
FROM gemma3:27b
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 32768
PARAMETER num_predict 4096
PARAMETER stop "<end_of_turn>"

SYSTEM """You are a meeting intelligence assistant. Extract structured notes from transcripts. Be concise, factual, do not editorialize."""
```

Build it:
```bash
ollama create meeting-notes -f Modelfile
```

Then set `OLLAMA_MODEL=meeting-notes` in your `.env`.

## Keep the Model Warm

Cold-start load is ~10s. Warm inference is ~0.17s. A 60x difference. Keep the model loaded:

```bash
export OLLAMA_KEEP_ALIVE="24h"
```

Add that to your shell profile (`.zshrc` or `.bashrc`) so it's always set when Ollama starts.

## Verify

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma3:27b",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}'
```

You should get a JSON response with a `message.content` field. That means Ollama is running and reachable.

## Point hybrid-meeting-notes at It

In your `.env`:
```bash
LLM_PROVIDER=ollama
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=gemma3:27b
```

Then process a test transcript:
```bash
python -m meeting_agent.cli process examples/sample_transcripts/standup.vtt
```

See `output/` for the generated markdown + JSON.

## Remote Access (Optional)

If you want to call Ollama from a different machine — a laptop, a cloud service, another user — the easiest approach is Tailscale (free) or a Caddy reverse proxy with API key auth. See [my hybrid-llm-deployment-guide repo](https://github.com/HarmanSingh-CCG/hybrid-llm-deployment-guide) for that setup in detail.
