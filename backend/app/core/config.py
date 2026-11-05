"""Configuration centrale (pydantic-settings).

Toutes les clés externes sont optionnelles : l'application démarre sans aucune
clé API. `feature_flags` expose au reste du code ce qui est réellement activable,
ce qui permet au frontend d'afficher honnêtement ce qui est opérationnel ou non
(voir §17 du cahier des charges : pas de capacité « simulée »).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Général
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # Sécurité
    secret_key: str = "change-me-dev-only"
    access_token_expire_minutes: int = 60

    # PostgreSQL
    postgres_user: str = "cyberai"
    postgres_password: str = "cyberai"
    postgres_db: str = "cyberai"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # Redis / Qdrant / MinIO
    redis_host: str = "redis"
    redis_port: int = 6379
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    minio_endpoint: str = "minio:9000"
    minio_root_user: str = "cyberai"
    minio_root_password: str = "cyberai-minio"
    minio_bucket: str = "cyberai"

    # LLM
    ollama_base_url: str = "http://host.docker.internal:11434"
    default_local_model: str = "qwen2.5:7b-instruct"
    default_embed_model: str = "nomic-embed-text"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    mistral_api_key: str = ""
    groq_api_key: str = ""
    default_remote_model: str = ""

    # OSINT / CTI
    shodan_api_key: str = ""
    virustotal_api_key: str = ""
    abuseipdb_api_key: str = ""
    securitytrails_api_key: str = ""
    censys_api_id: str = ""
    censys_api_secret: str = ""
    hibp_api_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def feature_flags(self) -> dict[str, bool]:
        """Ce qui est réellement activable compte tenu des clés présentes."""
        has_remote_llm = bool(
            self.anthropic_api_key
            or self.openai_api_key
            or self.mistral_api_key
            or self.groq_api_key
        )
        return {
            "llm_local": True,  # Ollama supposé disponible localement
            "llm_remote": has_remote_llm,
            "osint_shodan": bool(self.shodan_api_key),
            "osint_virustotal": bool(self.virustotal_api_key),
            "osint_abuseipdb": bool(self.abuseipdb_api_key),
            "osint_securitytrails": bool(self.securitytrails_api_key),
            "osint_censys": bool(self.censys_api_id and self.censys_api_secret),
            "osint_hibp": bool(self.hibp_api_key),
            # Capacités OSINT gratuites : toujours disponibles
            "osint_whois_dns": True,
            "osint_crtsh": True,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
