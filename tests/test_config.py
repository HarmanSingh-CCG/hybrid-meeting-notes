"""Config loader tests — env override behavior is subtle, test it."""

import os
from pathlib import Path

from meeting_agent.config import load_config


def test_defaults_without_file(tmp_path: Path, monkeypatch):
    # Ensure no leakage from real env
    for v in ("LLM_PROVIDER", "OLLAMA_MODEL", "MEETING_TEMPLATE"):
        monkeypatch.delenv(v, raising=False)
    cfg = load_config(None)
    assert cfg.provider == "ollama"
    assert cfg.ollama.endpoint == "http://localhost:11434"


def test_env_overrides_yaml(tmp_path: Path, monkeypatch):
    yaml_text = """
provider: ollama
ollama:
  model: gemma3:12b
"""
    p = tmp_path / "config.yaml"
    p.write_text(yaml_text)

    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    cfg = load_config(p)
    assert cfg.ollama.model == "llama3.2:3b"
    assert cfg.provider == "ollama"


def test_empty_env_does_not_override(tmp_path: Path, monkeypatch):
    yaml_text = """
provider: anthropic
"""
    p = tmp_path / "config.yaml"
    p.write_text(yaml_text)

    monkeypatch.setenv("LLM_PROVIDER", "")
    cfg = load_config(p)
    # Empty env string should not clobber yaml
    assert cfg.provider == "anthropic"
