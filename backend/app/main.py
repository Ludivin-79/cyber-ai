"""Point d'entrée de l'application CYBER AI (FastAPI).

Phase 0 : socle minimal mais réel — démarrage, CORS, journalisation,
endpoints de santé et d'état des capacités. Les modules métier (AI Core,
OSINT, CTI…) seront ajoutés dans les phases suivantes.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import chat, health
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="CYBER AI API",
        version=__version__,
        description="Plateforme d'IA cybersécurité / OSINT — socle Phase 0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)

    @app.get("/", tags=["root"])
    async def root() -> dict:
        return {"name": "CYBER AI", "version": __version__, "docs": "/docs"}

    return app


app = create_app()
