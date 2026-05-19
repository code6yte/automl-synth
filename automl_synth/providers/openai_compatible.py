"""OpenAI-compatible LLM provider."""

from __future__ import annotations

import json
from typing import Any

import httpx

from automl_synth.providers.base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """Generic OpenAI-compatible API provider."""

    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def complete_text(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def complete_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        text = await self.complete_text(messages, temperature=temperature, max_tokens=max_tokens)
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        return json.loads(cleaned)

    async def check_reachability(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    self.base_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return resp.status_code in (200, 404)
        except Exception:
            return False

    async def list_models(self) -> list[dict[str, str]]:
        """List available models from OpenAI-compatible endpoint."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
                models = []
                for m in data.get("data", []):
                    models.append({
                        "id": m.get("id", ""),
                        "name": m.get("id", ""),
                        "context_length": m.get("context_length", "N/A"),
                    })
                return models
        except Exception:
            return []
