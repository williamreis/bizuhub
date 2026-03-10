from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.interaction import InteractionRepository
from app.schemas.interaction import InteractionCreate, InteractionResponse

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionResponse)
def create_interaction(
    data: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = InteractionRepository(db)
    obj = repo.create(
        user_id=current_user.id,
        item_type=data.item_type.value,
        item_id=data.item_id,
        item_title=data.item_title,
        metadata=data.metadata,
    )
    return InteractionResponse(
        id=obj.id,
        user_id=obj.user_id,
        item_type=obj.item_type,
        item_id=obj.item_id,
        item_title=obj.item_title,
        timestamp=obj.timestamp,
        metadata=obj.metadata_,
    )
