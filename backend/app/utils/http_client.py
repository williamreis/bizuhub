"""Cliente HTTP com timeout e tratamento de erro para APIs externas."""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 15.0


async def get_json(
    url: str,
    params: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Optional[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        logger.warning("http_get_error url=%s error=%s", url, str(e))
        return None
