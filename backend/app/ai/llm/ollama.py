"""Fournisseur Ollama (modèles locaux) via l'API HTTP d'Ollama.

Aucune clé requise : suppose un Ollama joignable sur `OLLAMA_BASE_URL`.
Si Ollama est injoignable, `list_models` renvoie une liste vide et le routeur
bascule sur un autre fournisseur (echo) — sans prétendre qu'Ollama a répondu.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.ai.llm.base import LLMProvider, Message, ModelInfo


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def list_models(self) -> list[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                r.raise_for_status()
                data = r.json()
        except (httpx.HTTPError, json.JSONDecodeError):
            return []  # Ollama injoignable : on ne simule rien
        return [
            ModelInfo(
                id=m["name"],
                provider="ollama",
                kind="local",
                label=f"{m['name']} (local)",
            )
            for m in data.get("models", [])
        ]

    async def stream(
        self, messages: list[Message], model: str
    ) -> AsyncIterator[str]:
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    chunk = obj.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
                    if obj.get("done"):
                        break
