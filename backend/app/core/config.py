"""
Configuração centralizada. Todas as credenciais e segredos vêm exclusivamente de variáveis de ambiente.
Nunca definir valores sensíveis como default neste arquivo.
"""
from __future__ import annotations

from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação. Carrega de .env; falha se variáveis obrigatórias faltarem."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "BizuHub"
    debug: bool = False

    # Segurança - SECRET_KEY obrigatória (mín. 32 caracteres). Nunca commitar valor real.
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS - lista de origens permitidas (ex: http://localhost:3000)
    cors_origins: str = "http://localhost:3000"
    # Backend URL para o frontend chamar (ex: http://localhost:8000)
    api_url: str = "http://localhost:8000"

    # Banco (PostgreSQL recomendado em produção)
    database_url: str = "postgresql://bizuhub:bizuhub@localhost:5432/bizuhub"

    # APIs externas - chaves nunca no código, só em .env
    tmdb_api_key: str = ""
    google_books_api_key: str = ""

    # LLM (Groq)
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"

    # Telegram bot (webhook)
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""

    # Rate limiting
    rate_limit_per_minute: int = 60

    @field_validator("secret_key")
    @classmethod
    def secret_key_non_empty(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("SECRET_KEY deve ser definida em .env (ex.: .env.example)")
        if len(v) < 32:
            raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres")
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    return Settings()
