from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.interaction import ItemType


class InteractionCreate(BaseModel):
    item_type: ItemType
    item_id: str = Field(..., max_length=128)
    item_title: str = Field(..., max_length=512)
    metadata: Optional[dict[str, Any]] = None


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    item_type: str
    item_id: str
    item_title: str
    timestamp: datetime
    metadata: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    items: list[InteractionResponse]
    total: int
