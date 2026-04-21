# 04 — Configuring Hybrid Routing

Hybrid mode runs a primary provider with a fallback. It's useful when:
- Your local model is sufficient for 95% of meetings but you want insurance against outages
- You want latency guarantees: if local inference takes > N seconds, fail over to cloud
- You're experimenting with cloud quality on a subset of traffic

## Two Strategies

### `local-first` (default)

```
Try Ollama (with N-second timeout)  →  success: return
                                    →  timeout / error: try cloud  →  return
```

When to use: you have a working local setup but want cloud as a safety net.

### `cloud-first`

```
Try cloud                           →  success: return
                                    →  error: try local  →  return
```

When to use: you want cloud quality by default but don't want to fail if your API key is exhausted or provider is down.

## Configuration

```yaml
# config.yaml
provider: hybrid
hybrid:
  strategy: local-first          # or cloud-first
  local_provider: ollama
  cloud_provider: anthropic      # or openai / azure_openai
  local_timeout_seconds: 120     # how long to wait on local before failing over
```

Or via environment:
```bash
LLM_PROVIDER=hybrid
HYBRID_STRATEGY=local-first
HYBRID_LOCAL_PROVIDER=ollama
HYBRID_CLOUD_PROVIDER=anthropic
HYBRID_LOCAL_TIMEOUT_SECONDS=120
```

## How Failover Is Reported

Every meeting note JSON has a `provider_used` field. When hybrid fails over, the value is suffixed `(fallback)` — e.g. `anthropic (fallback)`. This makes it obvious which path served the request, so you can alert on unexpected fallbacks.

## What Hybrid Is NOT

- **Not automatic quality routing.** It doesn't send "hard" meetings to cloud and "easy" ones to local. The decision is purely "did primary succeed?" For complexity-based routing, see the sister repo [hybrid-llm-deployment-guide](https://github.com/HarmanSingh-CCG/hybrid-llm-deployment-guide) which implements exactly that.
- **Not a load balancer.** Each request is deterministic: primary first, fallback on failure. There's no probabilistic traffic splitting.
- **Not a caching layer.** Every call hits the LLM. If you want caching, add a provider wrapper.

## Honest Trade-off

Hybrid mode adds latency on failover cases — primary must fail or time out before secondary runs. For most post-meeting workflows, that's fine; nobody is waiting on the notes in real-time. For real-time use cases, set a tight `local_timeout_seconds` (e.g. 30) and accept some cases will skip local entirely.
