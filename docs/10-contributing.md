# 10 — Contributing

This is a template project. It's intentionally minimal and opinionated. Pull requests that make it more minimal or more opinionated are welcome; PRs that make it "bigger" for the sake of features are less so.

## Quick Yes-Please List

- **New LLM provider adapters** — follow the `LLMProvider` interface in `meeting_agent/providers/base.py`. Google Gemini, Groq, Mistral Cloud, DeepSeek, Together.ai, etc.
- **New transcript normalizers** — Zoom `.transcript.vtt` has slightly different conventions; Google Meet exports; Otter exports; Krisp exports.
- **Better templates** — share one that worked for your use case. Sales, legal, medical, research interviews, podcasts — all welcome.
- **Live transcription sources** — the current Teams source is post-meeting polling. Someone could plug in a desktop audio capture + Whisper streaming pipeline.
- **Tests** — test coverage is light. Normalizer tests, provider mocks, enhancer golden-file tests all welcome.

## Quick Think-First List

- **Before adding a new top-level feature**, open an issue to discuss. The goal is to stay a readable template, not a product.
- **Before adding a new dependency**, check whether stdlib or a smaller alternative can do it. Meeting the user where they are is the top priority.

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

pytest
```

## Code Style

- `ruff` for linting, `black` for formatting
- Type hints throughout
- Docstrings explain WHY, not WHAT (the code says what)

## Tests

```bash
pytest
```

Add tests for anything that could regress quietly — normalizers, prompt formatting, template rendering, provider payload shapes.

## Licensing

MIT. Contributing implies you're OK with your work being MIT-licensed.
