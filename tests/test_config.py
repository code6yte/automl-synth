"""Tests for config module."""

from automl_synth.config import load_config, validate_config, get_provider_type
from automl_synth.types import ProviderType


def test_load_config_defaults():
    cfg = load_config()
    assert "provider" in cfg
    assert "base_url" in cfg
    assert "model" in cfg
    assert "default_rows" in cfg
    assert cfg["default_rows"] == 300


def test_load_config_overrides():
    cfg = load_config(provider="ollama", model="llama3")
    assert cfg["provider"] == "ollama"
    assert cfg["model"] == "llama3"


def test_validate_config_missing_key():
    cfg = {
        "provider": "openrouter",
        "api_key": "",
        "base_url": "https://example.com",
        "model": "test",
    }
    errors = validate_config(cfg)
    assert len(errors) > 0


def test_validate_config_ollama_no_key():
    cfg = {
        "provider": "ollama",
        "api_key": "",
        "base_url": "http://localhost:11434",
        "model": "llama3",
    }
    errors = validate_config(cfg)
    assert len(errors) == 0


def test_get_provider_type():
    assert get_provider_type("openrouter") == ProviderType.OPENROUTER
    assert get_provider_type("ollama") == ProviderType.OLLAMA
    assert get_provider_type("openai_compatible") == ProviderType.OPENAI_COMPATIBLE
