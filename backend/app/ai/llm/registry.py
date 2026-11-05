"""Registre et routage des fournisseurs LLM.

Agrège les modèles disponibles et choisit le fournisseur à partir de l'id de
modèle demandé. Si aucun modèle réel n'est disponible, l'echo (stub) sert de
filet de sécurité pour que la plomberie reste testable.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.ai.llm.base import LLMProvider, Message, ModelInfo
from app.ai.llm.echo import EchoProvider
from app.ai.llm.ollama import OllamaProvider
from app.core.config import get_settings


class LLMRegistry:
    def __init__(self) -> None:
        settings = get_settings()
        self.ollama = OllamaProvider(settings.ollama_base_url)
        self.echo = EchoProvider()
        # Phase 2 : providers distants (Anthropic/OpenAI via LiteLLM) ajoutés ici,
        # activés selon settings.feature_flags["llm_remote"].

    async def list_models(self) -> list[ModelInfo]:
        models: list[ModelInfo] = []
        models.extend(await self.ollama.list_models())
        models.extend(await self.echo.list_models())  # toujours présent (stub)
        return models

    async def _provider_for(self, model: str) -> tuple[LLMProvider, str]:
        """Retourne (fournisseur, modèle) pour l'id demandé.

        - "echo" → stub
        - un modèle Ollama existant → Ollama
        - sinon → repli sur echo (jamais de simulation silencieuse)
        """
        if model == "echo":
            return self.echo, "echo"
        ollama_models = {m.id for m in await self.ollama.list_models()}
        if model in ollama_models:
            return self.ollama, model
        return self.echo, "echo"

    async def stream(
        self, messages: list[Message], model: str
    ) -> AsyncIterator[str]:
        provider, resolved = await self._provider_for(model)
        async for chunk in provider.stream(messages, resolved):
            yield chunk


_registry: LLMRegistry | None = None


def get_registry() -> LLMRegistry:
    global _registry
    if _registry is None:
        _registry = LLMRegistry()
    return _registry
