from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, RegisterRequest, TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == data.email.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")

    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        role="client",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user), user=user)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    return TokenResponse(access_token=create_access_token(user), user=user)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
