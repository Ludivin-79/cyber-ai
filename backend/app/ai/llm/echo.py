"""Fournisseur « echo » — STUB de développement.

But : permettre de tester la plomberie (streaming SSE, UI, historique) SANS
Ollama ni clé API. Il NE fait AUCUN raisonnement : il renvoie en streaming un
message explicite rappelant qu'aucun vrai modèle n'est configuré, suivi d'un
écho du dernier message utilisateur.

Il est volontairement étiqueté `kind="stub"` et `provider="echo"` pour que le
frontend n'affiche jamais ses sorties comme celles d'un vrai modèle
(exigence : aucune capacité simulée présentée comme opérationnelle).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from app.ai.llm.base import LLMProvider, Message, ModelInfo


class EchoProvider(LLMProvider):
    name = "echo"

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                id="echo",
                provider="echo",
                kind="stub",
                label="Echo (stub de test — aucun modèle réel)",
            )
        ]

    async def stream(
        self, messages: list[Message], model: str
    ) -> AsyncIterator[str]:
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        preface = (
            "[STUB echo — aucun modèle LLM n'est configuré. "
            "Configure Ollama ou une clé API pour obtenir de vraies réponses.] "
        )
        text = preface + f"Tu as écrit : {last_user}"
        for word in text.split(" "):
            yield word + " "
            await asyncio.sleep(0)  # laisse la main à la boucle d'évènements
