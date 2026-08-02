from schemas.user import UserManage
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from models.db import get_db
from models.user import User, Session, Subscription
from schemas.user import USER_STATUS, UserOut, SessionUserSchema
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from .jwt import decode
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from .redis import redis
from libs.logger import logger

from fastapi import Header
from permission import AppPermission

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/signin", auto_error=False)

async def get_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    header_token: Optional[str] = Depends(oauth2),
    cookie_token: Optional[str] = Cookie(None, alias="access_token"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> UserManage:
    token = header_token or cookie_token
    api_key_candidate = x_api_key

    if header_token and header_token.startswith("onyx_sec_"):
        api_key_candidate = header_token
        token = None

    if api_key_candidate:
        api_key_clean = api_key_candidate.strip()
        stmt = (
            select(User)
            .options(
                selectinload(User.current_subscription)
                .selectinload(Subscription.tier)
            )
            .where(User.api_key == api_key_clean, User.deleted_at.is_(None))
        )
        user_obj = await db.scalar(stmt)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key provided",
            )

        if user_obj.status != USER_STATUS.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive account",
            )

        from routers.v1.client.utils import get_user_permissions_and_limits
        perms, _ = get_user_permissions_and_limits(user_obj)
        if AppPermission.API_ACCESS not in perms and AppPermission.API_ACCESS.value not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API access is not enabled on your subscription tier. Upgrade to unlock API access.",
            )

        return UserManage.model_validate(user_obj)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token or API key",
        )
    data = decode(token)

    session_id = data.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    session_raw = await redis.get(f"onyx:session:{session_id}")
    session_data = None
    now = datetime.now(timezone.utc)

    if session_raw:
        session_data = SessionUserSchema.model_validate_json(session_raw)
    else:
        s = await db.scalar(
            select(Session)
            .options(
                selectinload(Session.user)
                .selectinload(User.current_subscription)
                .selectinload(Subscription.tier)
            )
            .where(Session.session_id == session_id, Session.expires_at > now.replace(tzinfo=None))
        )

        if not s:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired session",
            )

        session_data = SessionUserSchema.model_validate(s)
        try:
            json_session = session_data.model_dump_json()
            time_left = s.expires_at.replace(tzinfo=timezone.utc) - now if s.expires_at.tzinfo is None else s.expires_at - now
            seconds_left = int(time_left.total_seconds())
            if seconds_left > 0:
                await redis.set(f"onyx:session:{session_id}", json_session, ex=seconds_left)
        except Exception as err:
            logger.warning(f"Failed to cache session in Redis: {err}")

    user = session_data.user

    if user.status != USER_STATUS.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account",
        )

    return user

async def get_admin(
    user: UserManage = Depends(get_user),
) -> UserOut:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user