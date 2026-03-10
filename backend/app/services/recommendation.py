"""
Motor de recomendação: histórico do usuário + APIs TMDb e Google Books.
Cache simples em memória para evitar excesso de chamadas às APIs.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from app.core.config import get_settings
from app.models.interaction import ItemType
from app.repositories.interaction import InteractionRepository
from app.schemas.recommendation import RecommendationItem, RecommendationResponse
from app.utils.http_client import get_json

logger = logging.getLogger(__name__)

# Cache em memória (por tipo) - em produção considerar Redis
_cache: dict[str, list[dict[str, Any]]] = {}
_CACHE_TTL = 300  # 5 min - não implementado TTL aqui para MVP; reinício limpa cache


class RecommendationService:
    def __init__(self, interaction_repo: InteractionRepository):
        self.interaction_repo = interaction_repo
        self.settings = get_settings()

    async def get_recommendations(
        self,
        user_id: int,
        limit: int = 10,
        item_types: Optional[List[ItemType]] = None,
    ) -> RecommendationResponse:
        if item_types is None:
            item_types = [ItemType.movie, ItemType.series, ItemType.book]

        items: List[RecommendationItem] = []
        history = self.interaction_repo.get_by_user(user_id, limit=50)

        # Preferência baseada no histórico (mais do mesmo tipo)
        type_counts: dict[str, int] = {}
        for h in history:
            type_counts[h.item_type] = type_counts.get(h.item_type, 0) + 1

        for it in item_types:
            if it == ItemType.movie or it == ItemType.series:
                recs = await self._fetch_tmdb(limit=min(5, limit))
                items.extend(recs)
            else:
                recs = await self._fetch_google_books(limit=min(5, limit))
                items.extend(recs)

        # Deduplicate by item_id
        seen: set[str] = set()
        unique: List[RecommendationItem] = []
        for i in items:
            key = f"{i.item_type}:{i.item_id}"
            if key not in seen:
                seen.add(key)
                unique.append(i)
            if len(unique) >= limit:
                break

        # Se nenhuma API retornou dados, exibir recomendações de demonstração
        source = "tmdb+google_books"
        if not unique:
            unique = self._demo_recommendations(limit)
            source = "demo"

        return RecommendationResponse(items=unique[:limit], source=source)

    async def _fetch_tmdb(self, limit: int = 5) -> List[RecommendationItem]:
        api_key = self.settings.tmdb_api_key
        if not api_key:
            logger.warning("TMDb API key not set; returning empty movie/series recommendations")
            return []

        cache_key = "tmdb_trending"
        if cache_key in _cache:
            raw = _cache[cache_key][:limit]
        else:
            url = "https://api.themoviedb.org/3/trending/movie/day"
            data = await get_json(url, params={"api_key": api_key})
            if not data or "results" not in data:
                return []
            raw = data["results"][:limit]
            _cache[cache_key] = data["results"]

        result: List[RecommendationItem] = []
        base_img = "https://image.tmdb.org/t/p/w200"
        for r in raw:
            result.append(
                RecommendationItem(
                    item_type="movie",
                    item_id=str(r.get("id", "")),
                    title=r.get("title") or r.get("name") or "Unknown",
                    description=(r.get("overview") or "")[:500],
                    image_url=base_img + r["poster_path"] if r.get("poster_path") else None,
                    metadata={"release_date": r.get("release_date")},
                )
            )
        return result

    async def _fetch_google_books(self, limit: int = 5) -> List[RecommendationItem]:
        api_key = self.settings.google_books_api_key
        # Google Books permite requests sem key com cota menor
        params: dict[str, Any] = {"q": "fiction", "maxResults": limit}
        if api_key:
            params["key"] = api_key

        cache_key = "google_books_fiction"
        if cache_key in _cache:
            raw = _cache[cache_key][:limit]
        else:
            data = await get_json("https://www.googleapis.com/books/v1/volumes", params=params)
            if not data or "items" not in data:
                return []
            raw = data["items"]
            _cache[cache_key] = raw

        result: List[RecommendationItem] = []
        for r in raw:
            vol = r.get("volumeInfo", {})
            img = (vol.get("imageLinks") or {}).get("thumbnail", "")
            result.append(
                RecommendationItem(
                    item_type="book",
                    item_id=r.get("id", ""),
                    title=vol.get("title", "Unknown"),
                    description=(vol.get("description") or "")[:500],
                    image_url=img.replace("http://", "https://") if img else None,
                    metadata={"authors": vol.get("authors", [])},
                )
            )
        return result

    def _demo_recommendations(self, limit: int = 8) -> List[RecommendationItem]:
        """Recomendações de demonstração quando TMDb/Google Books não estão configurados."""
        return [
            RecommendationItem(
                item_type="movie",
                item_id="demo-1",
                title="Exemplo: Filme em destaque",
                description="Configure TMDB_API_KEY no .env para ver filmes reais.",
                image_url=None,
                metadata=None,
            ),
            RecommendationItem(
                item_type="series",
                item_id="demo-2",
                title="Exemplo: Série em destaque",
                description="Obtenha sua chave em themoviedb.org/settings/api",
                image_url=None,
                metadata=None,
            ),
            RecommendationItem(
                item_type="book",
                item_id="demo-3",
                title="Exemplo: Livro recomendado",
                description="Configure GOOGLE_BOOKS_API_KEY (opcional) para mais livros.",
                image_url=None,
                metadata=None,
            ),
        ][:limit]
