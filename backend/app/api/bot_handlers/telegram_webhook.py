"""
Webhook para receber atualizações do Telegram.
Validação do secret para garantir que a requisição veio do Telegram.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bot", tags=["bot"])


def _verify_telegram_webhook(body: bytes, secret: str) -> bool:
    if not secret:
        return False
    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, expected)


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    """
    Recebe POST do Telegram com a atualização.
    Telegram pode enviar X-Telegram-Bot-Api-Secret-Token se configurado.
    """
    settings = get_settings()
    body = await request.body()

    # Validação: se temos secret configurado, exige header
    if settings.telegram_webhook_secret:
        token = x_telegram_bot_api_secret_token or ""
        if not hmac.compare_digest(token, settings.telegram_webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook secret",
            )

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    # Processamento mínimo: log e resposta vazia (Telegram espera 200)
    update_id = data.get("update_id")
    message = data.get("message") or data.get("edited_message")
    if message:
        chat_id = message.get("chat", {}).get("id")
        text = (message.get("text") or "").strip()
        logger.info(
            "telegram_webhook update_id=%s chat_id=%s text_len=%d",
            update_id,
            chat_id,
            len(text),
        )
        # Opcional: enviar resposta via Bot API (requer telegram_bot_token)
        if settings.telegram_bot_token and chat_id:
            await _send_telegram_message(
                chat_id,
                "Olá! BizuHub: use o site para recomendações e chat com a IA.",
            )

    return {"ok": True}


async def _send_telegram_message(chat_id: int, text: str) -> None:
    import httpx
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json={"chat_id": chat_id, "text": text[:4096]})
    except Exception as e:
        logger.warning("telegram send message failed: %s", e)
