"""Endpoints de santé et d'état des capacités."""

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Liveness : l'application répond."""
    return {"status": "ok", "version": __version__}


@router.get("/capabilities")
async def capabilities() -> dict:
    """Expose honnêtement ce qui est réellement activable (selon les clés présentes).

    Le frontend s'en sert pour n'afficher comme « opérationnel » que ce qui l'est,
    conformément à l'exigence : aucune capacité simulée.
    """
    settings = get_settings()
    return {
        "environment": settings.environment,
        "features": settings.feature_flags,
    }
