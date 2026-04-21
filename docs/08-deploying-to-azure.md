# 08 — Deploying to Azure App Service

For teams already on Azure who want to deploy the agent as a proper web service — polling Teams in the background, accepting file uploads via an HTTP endpoint, delivering notes via email/Teams/Slack.

This is one specific deployment target. Alternatives: AWS Lambda / ECS, GCP Cloud Run, self-hosted Kubernetes, a systemd service on a Linux VM.

## When You Need This

- You want the Teams integration running 24/7 without a laptop always online
- Multiple users on your team should benefit, not just you
- You want the meeting notes delivered automatically to a shared location

## Prerequisites

- Azure subscription
- Entra ID app registration already done per [06-teams-integration.md](./06-teams-integration.md)
- Azure CLI installed locally: `brew install azure-cli`

## Tier Selection

- **B1 Basic** (~$13/mo) — fine for single-user POC, no VNet integration
- **S1 Standard** (~$55/mo) — needed if you want VNet integration (see below)
- **P1v3 Premium** (~$150/mo) — more RAM, better cold-start

## Connecting Azure to a Local LLM

If your LLM is running on a machine NOT on the internet (e.g., a Mac Mini on your LAN), Azure App Service cannot reach it by default. Three common patterns:

1. **Tailscale subnet router VM**: run a small Azure VM (B1ls ~$4/mo) with Tailscale and `advertise-routes`, then give App Service VNet integration. Requires Standard tier. Clean and secure.
2. **Tailscale sidecar in App Service**: containerize the agent and include Tailscale userspace-networking in the image. Free but requires Docker refactor.
3. **Public endpoint with API key auth**: expose your LLM via Caddy + DDNS or a Cloudflare Tunnel. Simplest, exposes more surface. Be honest about your compliance posture before picking this.

## Deploying the Code

```bash
# From repo root
rm -f /tmp/meeting-agent.zip
zip -r /tmp/meeting-agent.zip . \
  -x ".*" "__pycache__/*" "*.pyc" ".env" "*.zip" "*/__pycache__/*" "*/.DS_Store"

az webapp deploy \
  --resource-group <YOUR-RG> \
  --name <YOUR-APP-NAME> \
  --src-path /tmp/meeting-agent.zip \
  --type zip \
  --async true \
  --clean true
```

Always use `--clean true` — it prevents the "deployment in progress" lock that bites every deploy eventually.

## Startup Command

In App Service → Configuration → General settings → Startup command:

```
gunicorn --bind=0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker --timeout 600 app:app
```

(If you wrap this repo in a small aiohttp or FastAPI app — see `examples/fastapi_service.py` for a starter.)

## App Service Environment Variables

In App Service → Environment variables, set everything from your `.env`:

- `LLM_PROVIDER`, plus the provider-specific vars (Ollama endpoint, or Anthropic/OpenAI key)
- `TEAMS_*` if using Teams integration
- `MEETING_TEMPLATE`, `MEETING_AGENT_OUTPUT_DIR`

Restart the app after changes.

## Logs

```bash
az webapp log tail --resource-group <YOUR-RG> --name <YOUR-APP-NAME>
```

For a structured grep of just the agent's output:
```bash
az webapp log tail --resource-group <YOUR-RG> --name <YOUR-APP-NAME> 2>&1 | grep -i "meeting\|polling\|provider"
```

## Cost Snapshot

For a single user processing ~20 meetings/month:
- App Service B1: $13/mo
- (Optional) Tailscale subnet router B1ls VM: $4/mo
- Blob storage for outputs: <$1/mo
- LLM cost: $0 if local, ~$1/mo if cloud with cheap models
- **Total: ~$15-20/mo**

For comparison, consumer meeting-intelligence SaaS runs $10-20 PER USER PER MONTH. The economics compound in your favor as team size grows.
