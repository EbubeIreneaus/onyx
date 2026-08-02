import secrets
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.user import User
from schemas.user import UserOut
from libs.deps import get_user
from permission import AppPermission
from .utils import get_user_permissions_and_limits

router = APIRouter()

class ApiKeyResponse(BaseModel):
    api_key: Optional[str] = None
    has_api_access: bool
    created_at: Optional[datetime] = None

class ApiKeyGenerateResponse(BaseModel):
    api_key: str
    message: str

@router.get("/api-key", response_model=ApiKeyResponse)
async def get_api_key(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    perms, _ = get_user_permissions_and_limits(user)
    has_access = (
        AppPermission.API_ACCESS in perms
        or AppPermission.API_ACCESS.value in perms
    )

    user_obj = await db.scalar(select(User).where(User.user_id == user.user_id))
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return ApiKeyResponse(
        api_key=user_obj.api_key,
        has_api_access=has_access,
        created_at=user_obj.api_key_created_at,
    )

@router.post("/api-key/generate", response_model=ApiKeyGenerateResponse)
async def generate_api_key(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    perms, _ = get_user_permissions_and_limits(user)
    if AppPermission.API_ACCESS not in perms and AppPermission.API_ACCESS.value not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription tier does not allow Developer API Access. Please upgrade your plan.",
        )

    user_obj = await db.scalar(select(User).where(User.user_id == user.user_id))
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_token = f"onyx_sec_{secrets.token_urlsafe(32)}"
    user_obj.api_key = new_token
    user_obj.api_key_created_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user_obj)

    return ApiKeyGenerateResponse(
        api_key=new_token,
        message="API key generated successfully!",
    )

@router.post("/api-key/rotate", response_model=ApiKeyGenerateResponse)
async def rotate_api_key(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    perms, _ = get_user_permissions_and_limits(user)
    if AppPermission.API_ACCESS not in perms and AppPermission.API_ACCESS.value not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription tier does not allow Developer API Access. Please upgrade your plan.",
        )

    user_obj = await db.scalar(select(User).where(User.user_id == user.user_id))
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_token = f"onyx_sec_{secrets.token_urlsafe(32)}"
    user_obj.api_key = new_token
    user_obj.api_key_created_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user_obj)

    return ApiKeyGenerateResponse(
        api_key=new_token,
        message="API key rotated successfully. Previous token has been revoked.",
    )

@router.delete("/api-key")
async def revoke_api_key(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    user_obj = await db.scalar(select(User).where(User.user_id == user.user_id))
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_obj.api_key = None
    user_obj.api_key_created_at = None
    await db.commit()
    return {"success": True, "message": "API key revoked successfully"}
