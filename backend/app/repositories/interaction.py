from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from app.models.interaction import InteractionHistory, ItemType


class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        item_type: str,
        item_id: str,
        item_title: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> InteractionHistory:
        obj = InteractionHistory(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id,
            item_title=item_title,
            metadata_=metadata,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_user(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        item_type: Optional[ItemType] = None,
    ) -> List[InteractionHistory]:
        q = self.db.query(InteractionHistory).filter(InteractionHistory.user_id == user_id)
        if item_type is not None:
            q = q.filter(InteractionHistory.item_type == item_type.value)
        return q.order_by(InteractionHistory.timestamp.desc()).offset(offset).limit(limit).all()

    def count_by_user(self, user_id: int, item_type: Optional[ItemType] = None) -> int:
        q = self.db.query(InteractionHistory).filter(InteractionHistory.user_id == user_id)
        if item_type is not None:
            q = q.filter(InteractionHistory.item_type == item_type.value)
        return q.count()
