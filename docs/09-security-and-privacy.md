# 09 — Security and Privacy

This project was built because meeting content is sensitive and default SaaS handling of it was unacceptable. Here's the honest threat model.

## What Local-First Actually Gives You

When you run the agent with `LLM_PROVIDER=ollama` and a local Ollama server:
- Transcript bytes never leave your machine or your network
- No third-party SaaS has a copy of your notes
- Your prompts are not pooled into someone else's training data
- You control retention — if you delete the file, it's gone

## What Local-First Doesn't Give You

- **Does NOT make you SOC 2 / ISO 27001 compliant.** Compliance is about controls, documentation, and audits — not just where the data sits. Use this agent as ONE control among many.
- **Does NOT encrypt transcripts at rest automatically.** Your output directory is plain markdown and JSON. Use FileVault / LUKS / BitLocker on the host if you need at-rest encryption.
- **Does NOT protect against a compromised host.** If an attacker has root on the machine running the agent, they have your transcripts. Same as any local system.

## Threat Model by Provider

| Provider | Transcript Leaves Host? | Provider Sees Content? | Training Data Risk |
|---|---|---|---|
| `ollama` (local) | No | No | None |
| `ollama` (remote via Tailscale) | Only across your mesh | No | None |
| `anthropic` | Yes (HTTPS to Anthropic) | Yes | Anthropic states API data is not used for training by default |
| `openai` | Yes (HTTPS to OpenAI) | Yes | OpenAI states API data is not used for training for paid tier |
| `azure_openai` | Yes (HTTPS to your Azure tenant's OAI resource) | Microsoft sees metadata; content stays in your tenant's region | No training |
| `hybrid (local-first)` | Typically no; yes on fallback | Only on fallback | Only on fallback |

## Hardening Recommendations

### Always

- Treat the output directory as "confidential" — same classification as the underlying meetings
- Scrub templates before sharing — don't bake client/project names into the default template
- Rotate API keys every 90 days (Anthropic, OpenAI, Azure)
- Use environment variables, not checked-in config, for any API keys
- Add `.env`, `output/`, `raw_transcripts/` to `.gitignore` (already done)

### For Team Deployments

- Use Managed Identities on Azure instead of static API keys when possible
- Authenticate any HTTP endpoints with bearer tokens, not "security through obscurity"
- Set retention policies on blob storage (e.g., auto-delete raw transcripts after 7-14 days)
- Audit log every run — who kicked it off, which provider served it, how long it took

### For Compliance-Sensitive Deployments

- Keep `LLM_PROVIDER=ollama` hard-coded; do not enable cloud fallback
- Run the agent inside a network zone that has no egress to third-party LLM APIs
- Document the data flow in your System Security Plan / Risk Register
- Include the agent in your annual penetration test scope

## Redacting Before LLM Input (Future Work)

The current pipeline passes the full transcript to the LLM. For some use cases (attorney-client privileged content, HR discussions, medical conversations) you may want a pre-processing pass that redacts PII / privileged terms before the LLM sees anything.

This is not implemented. PRs welcome — the place to hook it in is right after normalization, before the enhancer. Typical approach: spaCy NER or a small local model doing a redaction pass.

## Responsible Disclosure

If you find a security issue in this code, open a GitHub issue with `[security]` in the title or reach out via the contact on my profile. This is a template project — bugs will exist. Please help make it safer.
