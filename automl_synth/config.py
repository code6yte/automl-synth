"""Configuration management for AutoML-Synth."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from platformdirs import user_config_path, user_cache_path

from automl_synth.types import ProviderType


def _find_env_file() -> Path | None:
    candidates = [
        Path.cwd() / ".env",
        user_config_path("automl-synth", ensure_exists=False) / ".env",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_config(
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    env_file = _find_env_file()
    if env_file:
        load_dotenv(env_file)

    llm_provider = provider or os.getenv("LLM_PROVIDER", "openrouter")
    llm_base_url = base_url or os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    llm_api_key = api_key or os.getenv("LLM_API_KEY", "")
    llm_model = model or os.getenv("LLM_MODEL", "openrouter/free")

    default_rows = int(os.getenv("AUTOML_SYNTH_DEFAULT_ROWS", "300"))
    search_enabled = os.getenv("AUTOML_SYNTH_SEARCH_ENABLED", "true").lower() == "true"
    max_search_results = int(os.getenv("AUTOML_SYNTH_MAX_SEARCH_RESULTS", "10"))
    output_dir = os.getenv("AUTOML_SYNTH_OUTPUT_DIR", "./output")
    log_level = os.getenv("AUTOML_SYNTH_LOG_LEVEL", "INFO")

    return {
        "provider": llm_provider,
        "base_url": llm_base_url,
        "api_key": llm_api_key,
        "model": llm_model,
        "default_rows": default_rows,
        "search_enabled": search_enabled,
        "max_search_results": max_search_results,
        "output_dir": output_dir,
        "log_level": log_level,
        "cache_dir": str(user_cache_path("automl-synth", ensure_exists=True)),
    }


def get_provider_type(provider_name: str) -> ProviderType:
    mapping = {
        "openrouter": ProviderType.OPENROUTER,
        "ollama": ProviderType.OLLAMA,
        "openai_compatible": ProviderType.OPENAI_COMPATIBLE,
        "openai-compatible": ProviderType.OPENAI_COMPATIBLE,
    }
    return mapping.get(provider_name.lower(), ProviderType.OPENROUTER)


def validate_config(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not cfg.get("api_key") and cfg["provider"] != "ollama":
        errors.append("LLM_API_KEY is required for non-Ollama providers")
    if not cfg.get("base_url"):
        errors.append("LLM_BASE_URL is required")
    if not cfg.get("model"):
        errors.append("LLM_MODEL is required")
    return errors
