# 03 — Setting Up Cloud Providers

If you're not running local inference, or you want hybrid routing with a cloud fallback, configure at least one cloud provider. All four are plug-and-play — set the env vars, change `LLM_PROVIDER`, done.

## Anthropic (Claude)

1. Get an API key at [console.anthropic.com](https://console.anthropic.com).
2. Set in `.env`:
   ```bash
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ANTHROPIC_MODEL=claude-sonnet-4-6
   ```
3. Install the SDK:
   ```bash
   pip install anthropic
   ```

Typical cost per 10,000-word meeting: ~$0.04 with Sonnet, ~$0.002 with Haiku.

## OpenAI

1. Get an API key at [platform.openai.com](https://platform.openai.com/api-keys).
2. Set in `.env`:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   ```
3. Install the SDK:
   ```bash
   pip install openai
   ```

Typical cost per 10,000-word meeting: ~$0.05 with gpt-4o-mini, ~$0.50 with gpt-4o.

## Azure OpenAI

For tenants with Azure OpenAI resource + deployment already provisioned:

1. Create a deployment in [Azure OpenAI Studio](https://oai.azure.com).
2. Set in `.env`:
   ```bash
   LLM_PROVIDER=azure_openai
   AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
   AZURE_OPENAI_API_KEY=<key>
   AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   ```
3. Uses the same `openai` SDK — no separate install.

## Google Gemini (Community Contribution Welcome)

Not included out of the box — add a `GeminiProvider` class under `meeting_agent/providers/` following the same shape as `OpenAIProvider`. PRs welcome.

## Cost Discipline Tips

- **Use the cheap model for summarization.** `gpt-4o-mini` / `claude-haiku` / `gemini-flash` are more than sufficient for meeting notes. Save frontier models for reasoning-heavy tasks.
- **Set a monthly budget alert** on your provider dashboard before turning this loose on a team.
- **Prefer hybrid routing** if you have any local capacity. 95% of meetings are small enough that local wins on cost and latency.

## Testing the Provider

```bash
python -m meeting_agent.cli process examples/sample_transcripts/standup.vtt
```

Check the `output/` — the generated JSON contains a `provider_used` field so you can confirm which backend actually served the request.
