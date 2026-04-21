# 01 — Why Local-First Meeting Intelligence

SaaS meeting-note tools (Granola, Otter, Fireflies, Zoom AI Companion, etc.) are excellent products. They're also fundamentally external services: your transcripts and summaries leave your boundary, sit on someone else's hardware, and flow through someone else's LLM.

For most teams that trade-off is worth it — they get a great UX in exchange for a reasonable data risk. But for a meaningful slice of teams, the economics and security invert:

- **Compliance-sensitive teams** (SOC 2, ISO 27001, HIPAA, government) where "meeting content leaves our tenant" is a hard constraint
- **Enterprises paying $10-20 per user per month** on meeting-intelligence SaaS
- **Teams with already-capable local hardware** (Apple Silicon, home-lab GPU boxes) running models that weren't feasible two years ago
- **Engineering-forward orgs** where the meeting notes are upstream inputs to other agents (BA, SA, CRM), not the final deliverable

The premise of this project:

> You can get 80% of Granola's quality for 5% of the cost using a local LLM on a Mac Mini — and keep every byte inside your tenant.

## What This Repo Is

A template. Not a product. You clone it, point it at a transcript, pick an LLM provider, and get structured meeting notes out. No SaaS signup, no training data pooled with other tenants, no vendor lock-in.

## What This Repo Is Not

- **Not a live transcription tool.** It processes transcripts AFTER a meeting ends (from Microsoft Teams, or any .vtt/.srt/.txt file). If you need in-meeting real-time capture, use Teams' built-in transcription or a desktop tool — this repo consumes its output.
- **Not a replacement for good note-takers.** The model summarizes what was said. If nothing useful was said, the notes will reflect that.
- **Not a magic compliance shield.** "Local LLM" means data stays on your hardware. It doesn't automatically make your data handling SOC 2 compliant. That's still on you.

## The Three Deployment Modes

1. **Local-only** — Ollama on your Mac. Zero API costs. Notes quality depends on the model you pick (Gemma 3 27B, Llama 3.1 70B, Qwen 2.5 72B, Mistral, etc.).
2. **Cloud-only** — OpenAI / Anthropic / Azure OpenAI. Fastest path for teams without local GPU capacity.
3. **Hybrid** — local first with cloud fallback on timeout or error. Best of both: typical traffic stays local, exceptional cases get frontier intelligence.

Pick based on your priorities. The same code serves all three.
