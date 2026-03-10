from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.limiter import limiter
from app.models.user import User
from app.models.interaction import ItemType
from app.repositories.interaction import InteractionRepository
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=30),
):
    repo = InteractionRepository(db)
    service = RecommendationService(repo)
    return await service.get_recommendations(user_id=current_user.id, limit=limit)


@router.get("/guest", response_model=RecommendationResponse)
@limiter.limit("30/minute")
async def get_recommendations_guest(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=15),
):
    """Recomendações públicas para visitantes (sem login)."""
    repo = InteractionRepository(db)
    service = RecommendationService(repo)
    return await service.get_recommendations(user_id=0, limit=limit)
