"""
BizuHub API. CORS restrito, rate limiting, JWT, validação Pydantic.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.endpoints import auth, chat, history, interactions, recommendations
from app.api.bot_handlers import telegram_webhook
from app.core.config import get_settings
from app.core.database import init_db
from app.core.limiter import limiter

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Plataforma SaaS de recomendação de filmes, séries e livros com IA conversacional.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(recommendations.router)
app.include_router(interactions.router)
app.include_router(history.router)
app.include_router(chat.router)
app.include_router(telegram_webhook.router)
