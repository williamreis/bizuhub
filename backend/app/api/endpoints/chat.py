from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.limiter import limiter
from app.core.database import get_db
from app.core.security import sanitize_string
from app.models.user import User
from app.repositories.interaction import InteractionRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_agent import LLMAgentService

router = APIRouter(prefix="/chat", tags=["chat"])
_rate = f"{get_settings().rate_limit_per_minute}/minute"
_guest_rate = "20/minute"


@router.post("", response_model=ChatResponse)
@limiter.limit(_rate)
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = sanitize_string(body.message, max_length=2000)
    if not message:
        return ChatResponse(reply="Por favor, envie uma mensagem válida.")

    interaction_repo = InteractionRepository(db)
    history = interaction_repo.get_by_user(current_user.id, limit=20)
    context_items = [
        {"item_type": h.item_type, "item_id": h.item_id, "item_title": h.item_title}
        for h in history
    ]

    agent = LLMAgentService()
    reply = await agent.chat(user_message=message, context_items=context_items)
    return ChatResponse(reply=reply)


@router.post("/guest", response_model=ChatResponse)
@limiter.limit(_guest_rate)
async def chat_guest(request: Request, body: ChatRequest):
    """Chat para visitantes (sem login). Respostas sem histórico do usuário."""
    message = sanitize_string(body.message, max_length=2000)
    if not message:
        return ChatResponse(reply="Por favor, envie uma mensagem válida.")
    agent = LLMAgentService()
    reply = await agent.chat(user_message=message, context_items=None)
    return ChatResponse(reply=reply)
