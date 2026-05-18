"""Provider factory."""

from __future__ import annotations

from automl_synth.config import get_provider_type
from automl_synth.providers.base import LLMProvider
from automl_synth.providers.ollama import OllamaProvider
from automl_synth.providers.openai_compatible import OpenAICompatibleProvider
from automl_synth.providers.openrouter import OpenRouterProvider
from automl_synth.types import ProviderType


def create_provider(
    provider_type: str,
    api_key: str = "",
    model: str = "",
    base_url: str = "",
) -> LLMProvider:
    ptype = get_provider_type(provider_type)
    if ptype == ProviderType.OPENROUTER:
        return OpenRouterProvider(api_key=api_key, model=model, base_url=base_url)
    elif ptype == ProviderType.OLLAMA:
        return OllamaProvider(model=model, base_url=base_url or "http://localhost:11434")
    elif ptype == ProviderType.OPENAI_COMPATIBLE:
        return OpenAICompatibleProvider(api_key=api_key, model=model, base_url=base_url)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
