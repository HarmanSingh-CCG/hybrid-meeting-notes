# hybrid-meeting-notes

**Local-first meeting intelligence with hybrid LLM routing.**

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Providers: Ollama, Anthropic, OpenAI, Azure OpenAI](https://img.shields.io/badge/providers-ollama%20%7C%20anthropic%20%7C%20openai%20%7C%20azure-green)
![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)
![Status: Production-tested](https://img.shields.io/badge/status-production--tested-brightgreen)

A template for turning meeting transcripts into structured, customizable notes using whatever LLM you want — local (Ollama), cloud (Anthropic / OpenAI / Azure OpenAI), or both with automatic failover. Sister project to [hybrid-llm-deployment-guide](https://github.com/HarmanSingh-CCG/hybrid-llm-deployment-guide).

---

## What This Is

Meeting-intelligence SaaS (Granola, Otter, Fireflies, Zoom AI Companion) charges $10-20 per user per month and sends your transcripts through their servers. For compliance-sensitive teams, large teams, or teams with a local GPU already sitting around, both of those are avoidable.

This repo gives you the pipeline as code:

```
Transcript  →  Normalize  →  LLM (local / cloud / hybrid)  →  Your template  →  Notes
```

No SaaS signup. No vendor lock-in. Your transcript never leaves your boundary unless you explicitly pick a cloud provider.

## What Sets It Apart

| | Local-only | SaaS Meeting AI | **This Project** |
|---|:-:|:-:|:-:|
| Data stays inside your boundary | ✅ | ❌ | ✅ (configurable) |
| Works when your ISP is down | ✅ | ❌ | ✅ |
| Access to frontier reasoning | ❌ | ✅ | ✅ (hybrid mode) |
| Customizable output format | ❌ | Partial | ✅ (your Jinja2 template) |
| $ cost at 30 users | Near zero | $300-600/mo | Near zero |
| You own the code | ✅ | ❌ | ✅ |

## Architecture

```
┌───────────────────┐
│  Transcript Source│   .vtt / .srt / .txt / .json / Microsoft Teams
└─────────┬─────────┘
          ▼
┌───────────────────┐
│    Normalizer     │   Strip timestamps/cue IDs; speaker + content only
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  Hybrid Router    │   local-first  →  cloud fallback
│                   │   cloud-first  →  local fallback
│                   │   or single provider
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  LLM Enhancement  │   Map-reduce chunking for long meetings
│                   │   Extracts: summary, actions, decisions, entities
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Template Renderer │   Your Jinja2 markdown template
└─────────┬─────────┘
          ▼
┌───────────────────┐
│     Outputs       │   Markdown note + JSON companion
└───────────────────┘
```

## Quick Start

Requires Python 3.11+.

```bash
git clone https://github.com/HarmanSingh-CCG/hybrid-meeting-notes.git
cd hybrid-meeting-notes
./setup.sh

# Pick your LLM provider
cp .env.example .env
# edit .env — set LLM_PROVIDER and credentials

# Process a sample transcript
python -m meeting_agent.cli process examples/sample_transcripts/standup.vtt

# See the output
open output/
```

## Three Modes, One Codebase

### Local (Ollama)
Zero API cost. Data never leaves your machine.
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=gemma3:27b
```
See [docs/02-setup-ollama.md](docs/02-setup-ollama.md).

### Cloud
Fastest path if you don't have local GPU capacity.
```bash
LLM_PROVIDER=anthropic        # or openai / azure_openai
ANTHROPIC_API_KEY=sk-ant-...
```
See [docs/03-setup-cloud-providers.md](docs/03-setup-cloud-providers.md).

### Hybrid (local + cloud failover)
Local first, cloud as safety net. Or vice versa.
```bash
LLM_PROVIDER=hybrid
HYBRID_STRATEGY=local-first
HYBRID_LOCAL_PROVIDER=ollama
HYBRID_CLOUD_PROVIDER=anthropic
HYBRID_LOCAL_TIMEOUT_SECONDS=120
```
See [docs/04-configuring-hybrid-routing.md](docs/04-configuring-hybrid-routing.md).

## Custom Output Templates

Drop any `.md` file into `templates/` with [Jinja2](https://jinja.palletsprojects.com/) placeholders:

```markdown
# {{ meeting.title }} — {{ meeting.date }}

## TL;DR
{{ summary.one_liner }}

## Action Items
{% for a in action_items %}
- **{{ a.owner }}** → {{ a.action }} ({{ a.due or "TBD" }})
{% endfor %}
```

Point config at it:
```yaml
template: ./templates/my_template.md
```

Four templates ship out of the box: `detailed_notes`, `executive_brief`, `standup_recap`, `client_meeting`. See [docs/05-custom-templates.md](docs/05-custom-templates.md) for the full variable reference.

## Project Structure

```
hybrid-meeting-notes/
├── meeting_agent/              # Core package
│   ├── cli.py                  # CLI entrypoint
│   ├── config.py               # YAML + env var config
│   ├── models.py               # Shared data models
│   ├── normalizers/            # VTT, SRT, TXT, JSON normalizers
│   ├── providers/              # Ollama, Anthropic, OpenAI, Azure OpenAI
│   ├── router.py               # Hybrid routing with failover
│   ├── enhancer.py             # LLM pipeline with map-reduce chunking
│   ├── renderer.py             # Jinja2 template rendering
│   ├── prompts.py              # LLM prompt templates
│   └── sources/                # Teams (via Graph), file upload
├── templates/                  # Ready-to-use Jinja2 templates
├── docs/                       # 10 numbered guides
├── examples/                   # Sample transcripts + example scripts
├── docker-compose.yml          # One-command local setup
├── Dockerfile
├── setup.sh                    # Friction-free install
├── config.example.yaml
├── .env.example
└── requirements.txt
```

## Documentation

- **[01 — Why Local-First](docs/01-why-local-first.md)** — philosophy + what this is and isn't
- **[02 — Setting Up Ollama](docs/02-setup-ollama.md)** — local LLM setup
- **[03 — Cloud Providers](docs/03-setup-cloud-providers.md)** — Anthropic, OpenAI, Azure OpenAI
- **[04 — Hybrid Routing](docs/04-configuring-hybrid-routing.md)** — failover strategies
- **[05 — Custom Templates](docs/05-custom-templates.md)** — writing your own output format
- **[06 — Microsoft Teams](docs/06-teams-integration.md)** — automatic transcript pulls from Graph
- **[07 — Docker Self-Hosting](docs/07-self-hosting-docker.md)**
- **[08 — Deploying to Azure](docs/08-deploying-to-azure.md)**
- **[09 — Security & Privacy](docs/09-security-and-privacy.md)** — honest threat model
- **[10 — Contributing](docs/10-contributing.md)**

## What's Built In

- [x] 4 LLM providers: Ollama (local), Anthropic, OpenAI, Azure OpenAI
- [x] Hybrid routing with configurable failover
- [x] Map-reduce chunking for long transcripts (>32K tokens)
- [x] 4 transcript formats: VTT, SRT, TXT, JSON
- [x] 4 output templates: detailed, executive brief, standup, client meeting
- [x] Microsoft Teams integration via Graph API
- [x] CLI + library usage
- [x] Docker compose setup

## Roadmap (Issues / PRs Welcome)

- [ ] Zoom transcript source
- [ ] Google Meet transcript source
- [ ] PII redaction pre-processing
- [ ] Google Gemini provider
- [ ] Groq / DeepSeek / Together.ai providers
- [ ] Web UI for template editing
- [ ] Delivery adapters: Slack, Teams, email, webhook

## License

MIT. See [LICENSE](LICENSE).

## Credits

Built by [Harman Singh](www.linkedin.com/in/harmanjot-singh-p-eng-pmp®-190341ab). Sister project to [hybrid-llm-deployment-guide](https://github.com/HarmanSingh-CCG/hybrid-llm-deployment-guide).
