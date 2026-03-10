"""
Agente conversacional com LangChain + Groq.
Respostas sobre filmes, séries e livros; pode usar histórico do usuário como contexto.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from app.core.config import get_settings
from app.core.security import sanitize_string

logger = logging.getLogger(__name__)


class LLMAgentService:
    def __init__(self):
        self.settings = get_settings()
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            try:
                from langchain_groq import ChatGroq
                api_key = self.settings.groq_api_key
                if not api_key:
                    raise ValueError("GROQ_API_KEY not set")
                self._llm = ChatGroq(
                    api_key=api_key,
                    model=self.settings.groq_model,
                    temperature=0.3,
                )
            except Exception as e:
                logger.exception("Failed to init Groq LLM: %s", e)
                raise
        return self._llm

    async def chat(
        self,
        user_message: str,
        context_items: Optional[List[dict[str, Any]]] = None,
    ) -> str:
        """Envia mensagem ao agente e retorna resposta. Entrada já deve estar sanitizada pelo endpoint."""
        safe_message = sanitize_string(user_message, max_length=2000)
        if not safe_message:
            return "Por favor, envie uma mensagem válida."

        system = (
            "Você é um assistente do BizuHub, especializado em recomendar e conversar sobre "
            "filmes, séries e livros. Seja conciso e amigável. Não invente dados de APIs; "
            "se não souber, diga que não tem essa informação."
        )
        if context_items:
            context_str = "\n".join(
                f"- {it.get('item_type', '')}: {it.get('item_title', '')} (id: {it.get('item_id', '')})"
                for it in context_items[:20]
            )
            system += f"\n\nHistórico recente do usuário (para contexto):\n{context_str}"

        try:
            llm = self._get_llm()
            from langchain_core.messages import HumanMessage, SystemMessage
            messages = [
                SystemMessage(content=system),
                HumanMessage(content=safe_message),
            ]
            response = await llm.ainvoke(messages)
            content = getattr(response, "content", "") or str(response)
            return sanitize_string(str(content), max_length=4000)
        except ValueError as e:
            if "GROQ_API_KEY" in str(e):
                return "Serviço de IA temporariamente indisponível. Configure GROQ_API_KEY no servidor."
            raise
        except Exception as e:
            logger.exception("LLM chat error: %s", e)
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
