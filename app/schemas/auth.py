from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenVerifyRequest(BaseModel):
    token: str


class TokenPayloadResponse(BaseModel):
    sub: str
    role: str
    exp: int
    type: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
