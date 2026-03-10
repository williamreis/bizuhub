"""
Segurança: JWT, hash de senha (bcrypt/passlib), sanitização básica.
Proteção contra timing attack na verificação de senha.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class TokenData(BaseModel):
    sub: str  # username
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Hash bcrypt válido (ex.: senha "dummy") para verify quando usuário não existe (timing attack).
_DUMMY_HASH = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"


def dummy_verify_password(plain_password: str) -> None:
    """Chame com a senha do request quando o usuário não existir, para evitar timing attack."""
    pwd_context.verify(plain_password, _DUMMY_HASH)


def create_access_token(data: dict[str, Any]) -> str:
    settings = get_settings()
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now.replace(minute=now.minute + settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[TokenData]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"verify_exp": True},
        )
        sub = payload.get("sub")
        if not sub:
            return None
        return TokenData(sub=sub, exp=payload.get("exp"), iat=payload.get("iat"))
    except JWTError:
        return None


def sanitize_string(value: str, max_length: int = 2000) -> str:
    """Remove caracteres perigosos e limita tamanho. Uso em inputs de texto (ex: chat)."""
    if not value or not isinstance(value, str):
        return ""
    value = value.strip()
    value = html.escape(value)
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    return value[:max_length]


def sanitize_for_log(value: str, max_length: int = 200) -> str:
    """Sanitiza string para exibir em logs (evitar injection em agregadores)."""
    if not value or not isinstance(value, str):
        return ""
    return re.sub(r"[\n\r\t]", " ", value.strip())[:max_length]
