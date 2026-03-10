from typing import Any, Optional

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    item_type: str = Field(..., description="movie | series | book")
    item_id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class RecommendationResponse(BaseModel):
    items: list[RecommendationItem]
    source: Optional[str] = None
