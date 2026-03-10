"""Signup e Login. Senha nunca retornada; proteção contra timing attack na autenticação."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import hash_password, verify_password, create_access_token, dummy_verify_password
from app.repositories.user import UserRepository
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["auth"])
_rate = f"{get_settings().rate_limit_per_minute}/minute"


@router.post("/signup", response_model=UserResponse)
@limiter.limit(_rate)
def signup(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    if repo.get_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe",
        )
    if repo.get_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado",
        )
    user = repo.create(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    return user


@router.post("/login", response_model=Token)
@limiter.limit(_rate)
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_username(data.username)
    if not user:
        dummy_verify_password(data.password)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
        )
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
        )
    token = create_access_token(data={"sub": user.username})
    return Token(access_token=token)