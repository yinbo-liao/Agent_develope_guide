from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User
from app.security.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TokenRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: TokenRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Authenticate and return JWT access/refresh tokens."""
    result = await session.execute(
        select(User).where(User.username == payload.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    extra = {"role": user.role, "tier": user.tier}
    access_token = create_access_token(subject=user.id, extra_claims=extra)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Exchange a refresh token for a new access/refresh token pair."""
    try:
        claims = decode_token(payload.refresh_token)
        if claims.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type.")
        user_id = claims.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Missing subject claim.")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=403, detail="Account not found or deactivated.")

    extra = {"role": user.role, "tier": user.tier}
    access_token = create_access_token(subject=user.id, extra_claims=extra)
    new_refresh = create_refresh_token(subject=user.id)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)
