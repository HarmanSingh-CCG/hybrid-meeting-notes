"""Example: demonstrate the hybrid router's local-first with cloud fallback.

Set up both Ollama (running locally) and a cloud API key, then run this.
The output JSON will tell you which provider actually served each call.

Run with Ollama stopped to force the fallback path.
"""

import asyncio

from meeting_agent.config import load_config
from meeting_agent.router import HybridRouter


async def main() -> None:
    cfg = load_config()
    cfg.provider = "hybrid"
    cfg.hybrid.strategy = "local-first"
    cfg.hybrid.local_provider = "ollama"
    cfg.hybrid.cloud_provider = "anthropic"
    cfg.hybrid.local_timeout_seconds = 30

    router = HybridRouter(cfg)

    response = await router.chat(
        system="You are a helpful assistant. Respond in JSON with key 'ok': true.",
        user="Confirm you received this message.",
    )
    print(f"Provider used: {response.provider}")
    print(f"Latency: {response.latency_seconds:.2f}s")
    print(f"Response: {response.content[:200]}")


if __name__ == "__main__":
    asyncio.run(main())
