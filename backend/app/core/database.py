from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models.base import Base
from app.models.user import User
from app.models.interaction import InteractionHistory

settings = get_settings()
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args["check_same_thread"] = False
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
