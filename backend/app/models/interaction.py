import enum
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ItemType(str, enum.Enum):
    movie = "movie"
    series = "series"
    book = "book"


class InteractionHistory(Base):
    __tablename__ = "interaction_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(16), nullable=False)  # ItemType value
    item_id: Mapped[str] = mapped_column(String(128), nullable=False)
    item_title: Mapped[str] = mapped_column(String(512), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="interactions")
