# LinkedIn Post Draft — hybrid-meeting-notes launch

Three variants below — pick the one that best matches the tone of your previous post, or I can adjust further. All are under LinkedIn's 3,000-character limit.

---

## VARIANT A — Build-in-Public / Technical

Last quarter I open-sourced a hybrid LLM deployment guide (local Gemma + Claude fallback on a Mac Mini).

This weekend I built the natural follow-up: **hybrid-meeting-notes** — a local-first meeting intelligence agent with the same hybrid routing pattern.

Why: meeting-intelligence SaaS charges $10-20 per user per month and sends your transcripts to their servers. For compliance-sensitive teams (SOC 2, ISO 27001, HIPAA), that's not workable. And for teams with a Mac Mini or GPU box already sitting around, the economics don't make sense either.

What it does:
• Point it at a Teams meeting transcript (or any .vtt / .srt / .txt / .json file)
• It normalizes, chunks for long meetings, runs through an LLM, and writes structured notes in your custom markdown template
• Supports Ollama, Anthropic, OpenAI, and Azure OpenAI — or hybrid mode with local-first cloud failover
• Your transcripts never leave your boundary in local-only mode

Cost math that made me build it: Granola is ~$5,000/yr for a 30-person team. This runs on a $4/mo Azure VM + local Gemma on a Mac Mini. ~40x cheaper, same data sovereignty as a local tool.

It's a template, not a product. You clone it, point it at a transcript, pick a provider, get notes. MIT licensed. Ships with 4 customizable output templates and 10 guides covering setup, hybrid routing, Teams integration, Azure deploy, and an honest security threat model.

Big lessons from the build I wrote up in the repo:
1. Teams transcript subscriptions require an encryption cert setup that's easy to miss in the docs — polling is simpler for most cases
2. `getAllTranscripts` is a `/beta/` endpoint function, not `/v1.0/`, with `startDateTime` as a function parameter (not `$filter`)
3. Azure App Service in its default configuration can't reach private IPs — you need a Tailscale subnet router, Private Endpoint, or sidecar

Repo: https://github.com/HarmanSingh-CCG/hybrid-meeting-notes
Sister project: https://github.com/HarmanSingh-CCG/hybrid-llm-deployment-guide

If you build with it, tell me what templates you write — curious which verticals this resonates with most.

#GenAI #OpenSource #LocalLLM #Ollama #Meetings #Privacy #Python

---

## VARIANT B — Problem-First / Business-Framed

Your meeting notes don't need to live on someone else's server.

Most teams I talk to are quietly paying $10-20 per user per month for a SaaS meeting-intelligence tool. The ones in regulated industries (healthcare, finance, public sector, defense-adjacent) also have an awkward conversation to have with their compliance officer about where the content actually goes.

I kept hearing the same thing: "we like the product but the data handling doesn't fit our posture."

So I built a template. MIT licensed. Open source.

**hybrid-meeting-notes**: point it at a meeting transcript, get structured notes back in any template you design. Runs on:
• Local LLM (Ollama — Gemma, Llama, Mistral, Qwen, etc.) — data never leaves your machine
• Cloud LLM (Anthropic, OpenAI, Azure OpenAI) — for teams without local capacity
• Hybrid — local first, automatic cloud fallback on timeout

The economics on a 30-person team: ~$5,000/yr saved vs the typical SaaS alternative. The compliance story: your content never touches a third party if you don't want it to. The ownership story: you run the code.

This is the second open-source project in a series on hybrid local-cloud AI deployment. The first was a hybrid LLM router for Mac Mini (https://github.com/HarmanSingh-CCG/hybrid-llm-deployment-guide). This one is the application layer on top.

Included: 4 LLM providers, 4 output templates, Microsoft Teams integration via Graph API, Docker compose setup, 10 guides covering local setup through Azure deployment, and an honest security threat model.

Repo: https://github.com/HarmanSingh-CCG/hybrid-meeting-notes

Take it, fork it, make it yours. If you publish a good template or a new provider adapter, send a PR.

#AI #OpenSource #MeetingProductivity #DataSovereignty #LocalFirst

---

## VARIANT C — Short / Punchy

New open-source drop: **hybrid-meeting-notes**.

Local-first meeting intelligence with hybrid LLM routing. Runs on your Mac with Ollama, or Anthropic/OpenAI/Azure OpenAI if you prefer cloud, or both with automatic failover.

Why: meeting-intelligence SaaS is $10-20/user/mo and sends your transcripts to a third party. For compliance-sensitive teams that's a non-starter. This gives you the pipeline as code.

• MIT licensed
• 4 LLM providers out of the box
• Customizable Jinja2 output templates (4 included)
• Microsoft Teams integration
• 10 docs covering setup, routing, Teams Graph API, Azure deploy, security

Sister project to my hybrid LLM deployment guide from last quarter.

Repo: https://github.com/HarmanSingh-CCG/hybrid-meeting-notes

Take it, fork it, make it yours.

#AI #OpenSource #LocalLLM
