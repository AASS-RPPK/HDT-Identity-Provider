from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    TokenVerifyRequest,
    TokenPayloadResponse,
    UserResponse,
)
from app.services.auth import (
    authenticate_user,
    issue_tokens,
    refresh_access_token,
    register_user,
    verify_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Register a new user account."""
    try:
        user = register_user(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate and receive access + refresh tokens."""
    try:
        user = authenticate_user(db, request.username, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    tokens = issue_tokens(db, user)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange a refresh token for a new access + refresh token pair."""
    try:
        tokens = refresh_access_token(db, request.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return TokenResponse(**tokens)


@router.post("/verify", response_model=TokenPayloadResponse)
def verify(
    request: TokenVerifyRequest,
) -> TokenPayloadResponse:
    """Verify an access token and return its payload.

    This endpoint is called by the API Gateway (and other microservices)
    to validate incoming Bearer tokens without needing the JWT secret.
    """
    try:
        payload = verify_token(request.token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return TokenPayloadResponse(**payload)
