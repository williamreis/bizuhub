from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.interaction import ItemType
from app.repositories.interaction import InteractionRepository
from app.schemas.interaction import HistoryResponse, InteractionResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    item_type: str | None = Query(None, regex="^(movie|series|book)$"),
):
    repo = InteractionRepository(db)
    it_type = ItemType(item_type) if item_type else None
    items = repo.get_by_user(current_user.id, limit=limit, offset=offset, item_type=it_type)
    total = repo.count_by_user(current_user.id, item_type=it_type)
    return HistoryResponse(
        items=[InteractionResponse(
            id=o.id,
            user_id=o.user_id,
            item_type=o.item_type,
            item_id=o.item_id,
            item_title=o.item_title,
            timestamp=o.timestamp,
            metadata=o.metadata_,
        ) for o in items],
        total=total,
    )
