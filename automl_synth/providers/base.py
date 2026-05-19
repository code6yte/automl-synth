"""Base LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete_text(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Complete a chat conversation and return text response."""
        ...

    @abstractmethod
    async def complete_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Complete a chat conversation expecting JSON response."""
        ...

    @abstractmethod
    async def check_reachability(self) -> bool:
        """Check if the provider endpoint is reachable."""
        ...

    async def list_models(self) -> list[dict[str, str]]:
        """List available models. Returns empty list if not supported."""
        return []
