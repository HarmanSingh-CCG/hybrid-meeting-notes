"""Configuration loader — merges YAML config with environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OllamaConfig:
    endpoint: str = "http://localhost:11434"
    model: str = "gemma3:27b"
    api_key: str | None = None
    timeout_seconds: int = 300


@dataclass
class AnthropicConfig:
    api_key: str = ""
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096


@dataclass
class OpenAIConfig:
    api_key: str = ""
    model: str = "gpt-4o-mini"


@dataclass
class AzureOpenAIConfig:
    endpoint: str = ""
    api_key: str = ""
    deployment: str = ""
    api_version: str = "2024-08-01-preview"


@dataclass
class HybridConfig:
    strategy: str = "local-first"  # local-first | cloud-first
    local_provider: str = "ollama"
    cloud_provider: str = "anthropic"
    local_timeout_seconds: int = 120


@dataclass
class TeamsConfig:
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    target_user_id: str = ""
    poll_interval_seconds: int = 300


@dataclass
class MetadataConfig:
    title_regex: str = r"^\[([^-]+)-([^\]]+)\]"


@dataclass
class Config:
    provider: str = "ollama"
    template: str = "./templates/detailed_notes.md"
    output_dir: str = "./output"
    chunk_token_budget: int = 18_000
    chunk_overlap_tokens: int = 500
    temperature: float = 0.3
    max_output_tokens: int = 4096

    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    anthropic: AnthropicConfig = field(default_factory=AnthropicConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    azure_openai: AzureOpenAIConfig = field(default_factory=AzureOpenAIConfig)
    hybrid: HybridConfig = field(default_factory=HybridConfig)
    teams: TeamsConfig = field(default_factory=TeamsConfig)
    source_type: str = "file"  # file | teams
    metadata: MetadataConfig = field(default_factory=MetadataConfig)


def load_config(path: str | Path | None = None) -> Config:
    """Load config from YAML file (if provided) + environment variables.
    YAML values are the base; env vars override where set."""
    data: dict[str, Any] = {}
    if path:
        p = Path(path)
        if p.exists():
            data = yaml.safe_load(p.read_text()) or {}

    cfg = Config(
        provider=data.get("provider", "ollama"),
        template=data.get("template", "./templates/detailed_notes.md"),
        output_dir=data.get("output_dir", "./output"),
        chunk_token_budget=int(data.get("chunk_token_budget", 18_000)),
        chunk_overlap_tokens=int(data.get("chunk_overlap_tokens", 500)),
        temperature=float(data.get("temperature", 0.3)),
        max_output_tokens=int(data.get("max_output_tokens", 4096)),
        source_type=(data.get("source") or {}).get("type", "file"),
    )

    ollama = data.get("ollama", {})
    cfg.ollama = OllamaConfig(
        endpoint=ollama.get("endpoint", "http://localhost:11434"),
        model=ollama.get("model", "gemma3:27b"),
        api_key=ollama.get("api_key"),
        timeout_seconds=int(ollama.get("timeout_seconds", 300)),
    )

    ant = data.get("anthropic", {})
    cfg.anthropic = AnthropicConfig(
        api_key=ant.get("api_key", ""),
        model=ant.get("model", "claude-sonnet-4-6"),
        max_tokens=int(ant.get("max_tokens", 4096)),
    )

    oai = data.get("openai", {})
    cfg.openai = OpenAIConfig(
        api_key=oai.get("api_key", ""),
        model=oai.get("model", "gpt-4o-mini"),
    )

    azo = data.get("azure_openai", {})
    cfg.azure_openai = AzureOpenAIConfig(
        endpoint=azo.get("endpoint", ""),
        api_key=azo.get("api_key", ""),
        deployment=azo.get("deployment", ""),
        api_version=azo.get("api_version", "2024-08-01-preview"),
    )

    hyb = data.get("hybrid", {})
    cfg.hybrid = HybridConfig(
        strategy=hyb.get("strategy", "local-first"),
        local_provider=hyb.get("local_provider", "ollama"),
        cloud_provider=hyb.get("cloud_provider", "anthropic"),
        local_timeout_seconds=int(hyb.get("local_timeout_seconds", 120)),
    )

    teams = data.get("teams", {})
    cfg.teams = TeamsConfig(
        tenant_id=teams.get("tenant_id", ""),
        client_id=teams.get("client_id", ""),
        client_secret=teams.get("client_secret", ""),
        target_user_id=teams.get("target_user_id", ""),
        poll_interval_seconds=int(teams.get("poll_interval_seconds", 300)),
    )

    meta = data.get("metadata", {})
    cfg.metadata = MetadataConfig(title_regex=meta.get("title_regex", cfg.metadata.title_regex))

    # Env var overrides (only when set + non-empty)
    _apply_env_overrides(cfg)
    return cfg


def _apply_env_overrides(cfg: Config) -> None:
    def _get(name: str, default: str | None = None) -> str | None:
        v = os.getenv(name)
        return v if v not in (None, "") else default

    if v := _get("LLM_PROVIDER"): cfg.provider = v
    if v := _get("MEETING_TEMPLATE"): cfg.template = v
    if v := _get("MEETING_AGENT_OUTPUT_DIR"): cfg.output_dir = v

    if v := _get("OLLAMA_ENDPOINT"): cfg.ollama.endpoint = v
    if v := _get("OLLAMA_MODEL"): cfg.ollama.model = v
    if v := _get("OLLAMA_API_KEY"): cfg.ollama.api_key = v

    if v := _get("ANTHROPIC_API_KEY"): cfg.anthropic.api_key = v
    if v := _get("ANTHROPIC_MODEL"): cfg.anthropic.model = v

    if v := _get("OPENAI_API_KEY"): cfg.openai.api_key = v
    if v := _get("OPENAI_MODEL"): cfg.openai.model = v

    if v := _get("AZURE_OPENAI_ENDPOINT"): cfg.azure_openai.endpoint = v
    if v := _get("AZURE_OPENAI_API_KEY"): cfg.azure_openai.api_key = v
    if v := _get("AZURE_OPENAI_DEPLOYMENT"): cfg.azure_openai.deployment = v
    if v := _get("AZURE_OPENAI_API_VERSION"): cfg.azure_openai.api_version = v

    if v := _get("HYBRID_STRATEGY"): cfg.hybrid.strategy = v
    if v := _get("HYBRID_LOCAL_PROVIDER"): cfg.hybrid.local_provider = v
    if v := _get("HYBRID_CLOUD_PROVIDER"): cfg.hybrid.cloud_provider = v
    if v := _get("HYBRID_LOCAL_TIMEOUT_SECONDS"):
        cfg.hybrid.local_timeout_seconds = int(v)

    if v := _get("TEAMS_TENANT_ID"): cfg.teams.tenant_id = v
    if v := _get("TEAMS_CLIENT_ID"): cfg.teams.client_id = v
    if v := _get("TEAMS_CLIENT_SECRET"): cfg.teams.client_secret = v
    if v := _get("TEAMS_TARGET_USER_ID"): cfg.teams.target_user_id = v
    if v := _get("TEAMS_POLL_INTERVAL_SECONDS"):
        cfg.teams.poll_interval_seconds = int(v)
