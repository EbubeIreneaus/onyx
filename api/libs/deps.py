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

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/signin", auto_error=False)

async def get_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    header_token: Optional[str] = Depends(oauth2),
    cookie_token: Optional[str] = Cookie(None, alias="access_token")
) -> UserManage:
    token = header_token or cookie_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
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