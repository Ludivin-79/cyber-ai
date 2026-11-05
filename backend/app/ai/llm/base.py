"""Contrats communs de la couche LLM.

Toute la plateforme passe par l'interface `LLMProvider` : aucun module métier
n'importe un SDK de fournisseur en direct (voir skill `llm-integration`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Literal

from pydantic import BaseModel

Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    role: Role
    content: str


class ModelInfo(BaseModel):
    """Décrit un modèle disponible, exposé au frontend."""

    id: str                 # identifiant utilisé à l'appel (ex. "qwen2.5:7b-instruct")
    provider: str           # "ollama" | "echo" | "anthropic" | ...
    kind: Literal["local", "remote", "stub"]
    label: str              # libellé lisible


class LLMProvider(ABC):
    """Interface commune à tous les fournisseurs."""

    name: str

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        ...

    @abstractmethod
    async def stream(
        self, messages: list[Message], model: str
    ) -> AsyncIterator[str]:
        """Génère la réponse token par token (ou fragment par fragment)."""
        # Les implémentations sont des générateurs asynchrones.
        raise NotImplementedError
        yield ""  # pragma: no cover
