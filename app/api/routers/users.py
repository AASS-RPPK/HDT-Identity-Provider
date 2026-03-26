from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserListResponse, UserResponse
from app.services.auth import get_user_by_id, list_users

router = APIRouter(prefix="/auth/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def get_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> UserListResponse:
    """List all registered users (admin-level endpoint)."""
    users, total = list_users(db, limit=limit, offset=offset)
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Get a single user by ID."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)
