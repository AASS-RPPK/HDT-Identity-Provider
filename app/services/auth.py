from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models import RefreshToken, User, UserRole
from app.schemas.auth import RegisterRequest


def register_user(db: Session, request: RegisterRequest) -> User:
    existing = db.execute(
        select(User).where((User.email == request.email) | (User.username == request.username))
    ).scalars().first()
    if existing:
        field = "email" if existing.email == request.email else "username"
        raise ValueError(f"A user with this {field} already exists")

    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=UserRole.USER.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.execute(
        select(User).where(User.username == username)
    ).scalars().first()

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid username or password")

    if not user.is_active:
        raise ValueError("User account is deactivated")

    return user


def issue_tokens(db: Session, user: User) -> dict[str, str]:
    """Create an access + refresh token pair and persist the refresh token."""
    payload = {"sub": user.id, "role": user.role}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at))
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token_str: str) -> dict[str, str]:
    """Validate a refresh token, revoke it, and issue a new token pair."""
    try:
        payload = decode_token(refresh_token_str)
    except Exception as exc:
        raise ValueError("Invalid or expired refresh token") from exc

    if payload.get("type") != "refresh":
        raise ValueError("Token is not a refresh token")

    stored = db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token_str)
    ).scalars().first()

    if not stored or stored.revoked:
        raise ValueError("Refresh token has been revoked or does not exist")

    if stored.expires_at < datetime.now(timezone.utc):
        raise ValueError("Refresh token has expired")

    # Revoke the old refresh token (rotation).
    stored.revoked = True

    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise ValueError("User not found or deactivated")

    tokens = issue_tokens(db, user)
    return tokens


def verify_token(token: str) -> dict:
    """Decode an access token and return its payload. Used by the gateway."""
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise ValueError(f"Token verification failed: {exc}") from exc

    if payload.get("type") != "access":
        raise ValueError("Token is not an access token")

    return payload


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def list_users(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[User], int]:
    total = len(db.execute(select(User).with_only_columns(User.id)).all())
    stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    users = list(db.execute(stmt).scalars().all())
    return users, total
