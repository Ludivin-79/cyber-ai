"""Endpoints de chat : liste des modèles + streaming SSE.

Le streaming utilise Server-Sent Events (SSE). Chaque fragment est émis sous la
forme `data: {"delta": "..."}` et le flux se termine par `data: [DONE]`.
"""

from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.ai.llm.base import Message
from app.ai.llm.registry import get_registry

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str = "echo"


@router.get("/models")
async def models() -> dict:
    """Liste des modèles réellement disponibles (Ollama détecté + stub echo)."""
    registry = get_registry()
    return {"models": [m.model_dump() for m in await registry.list_models()]}


@router.post("/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    registry = get_registry()

    async def event_source():
        try:
            async for delta in registry.stream(req.messages, req.model):
                yield f"data: {json.dumps({'delta': delta})}\n\n"
        except Exception as exc:  # noqa: BLE001 — on remonte une erreur propre au client
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
