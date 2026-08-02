import json
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Response, Depends, Header, Cookie, status
from pydantic import EmailStr
from pwdlib import PasswordHash
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.user import User as UserModel, Session as SessionModel
from schemas.user import (
    UserCreate,
    LoginSchema,
    ChangePassIn,
    ResetLinkIn,
    ResetPassIn,
    SessionUserSchema,
    UserOut,
    USER_STATUS,
)
from libs.deps import get_user
from libs.jwt import encode
from libs.redis import redis
from libs.limiter import limiter
from setting import settings
from workers.config import get_arq_pool
from libs.logger import logger

router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_TOKEN_EXP = 6000
REFRESH_TOKEN_EXP = 30

password_hash = PasswordHash.recommended()

env = settings.APP_ENV
cookie_is_secure = True if env == "production" else False
cookie_domain = f".{settings.DOMAIN_NAME}" if env == "production" else None

@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserOut = Depends(get_user)):
    return current_user

@router.post("/signup", status_code=status.HTTP_201_CREATED)

@limiter.limit("25/hour", error_message="Too many requests, try again later")
async def signup(
    request: Request,
    response: Response,
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    email = body.email.lower()
    existing_user = await db.scalar(select(UserModel).where(UserModel.email == email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    hashed_password = password_hash.hash(body.password)
    refresh_token = secrets.token_urlsafe(30)
    r_token_hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    
    now = datetime.now(timezone.utc)
    access_token_expires_at = now + timedelta(seconds=ACCESS_TOKEN_EXP)
    refresh_token_expires_at = now + timedelta(days=REFRESH_TOKEN_EXP)

    new_user = UserModel(
        fullname=body.fullname,
        email=email,
        password=hashed_password,
    )
    
    client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else (request.client.host if request.client else "127.0.0.1")

    new_session = SessionModel(
        user=new_user,
        refresh_token=r_token_hashed,
        expires_at=refresh_token_expires_at.replace(tzinfo=None),
        ip_address=client_ip,
        user_agent=user_agent,
    )

    db.add_all([new_user, new_session])
    await db.commit()

    jwt_payload = {
        "sub": str(new_user.user_id),
        "session_id": str(new_session.session_id),
        "fullname": new_user.fullname,
        "email": new_user.email,
        "exp": access_token_expires_at,
    }
    token = encode(jwt_payload)


    response.set_cookie(
        "access_token",
        token,
        expires=access_token_expires_at,
        samesite="lax",
        secure=cookie_is_secure,
        domain=cookie_domain
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        expires=refresh_token_expires_at,
        httponly=True,
        samesite="lax",
        secure=cookie_is_secure,
        domain=cookie_domain
    )

    try:
        session_data = SessionUserSchema.model_validate(new_session).model_dump_json()
        await redis.set(f"onyx:session:{new_session.session_id}", session_data, ex=ACCESS_TOKEN_EXP)
    except Exception as err:
        logger.warning(f"Failed to cache session in Redis for user {email}: {err}")

    try:
        arq = await get_arq_pool()
        await arq.enqueue_job("update_session", str(new_session.session_id), user_agent, _queue_name="onyx")
        await arq.enqueue_job("send_welcome_email", email, body.fullname, _queue_name="onyx")
    except Exception as err:
        logger.warning(f"Failed to enqueue signup background jobs for user {email}: {err}")

    return {"success": True, "token": token, "refresh_token": refresh_token}

@router.post("/signin")
@limiter.limit("30/hour", error_message="Too many requests, try again later")
async def signin(
    request: Request,
    response: Response,
    body: LoginSchema,
    db: AsyncSession = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    email = body.email.lower()
    fake_pass = password_hash.hash("fake_password")

    stmt = select(UserModel).options(
        selectinload(UserModel.current_subscription)
    ).where(UserModel.email == email)
    user = await db.scalar(stmt)

    target_hash = user.password if user else fake_pass
    valid_password = password_hash.verify(body.password, target_hash)

    if not user or not valid_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect email or password",
        )

    if user.status != USER_STATUS.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account status is {user.status.value}",
        )

    client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else (request.client.host if request.client else "127.0.0.1")
    refresh_token = secrets.token_urlsafe(30)
    r_token_hashed = hashlib.sha256(refresh_token.encode()).hexdigest()

    now = datetime.now(timezone.utc)
    access_token_expires_at = now + timedelta(seconds=ACCESS_TOKEN_EXP)
    refresh_token_expires_at = now + timedelta(days=REFRESH_TOKEN_EXP)

    session = SessionModel(
        user=user,
        refresh_token=r_token_hashed,
        expires_at=refresh_token_expires_at.replace(tzinfo=None),
        ip_address=client_ip,
        user_agent=user_agent,
    )

    db.add(session)
    await db.commit()

    jwt_payload = {
        "sub": str(user.user_id),
        "session_id": str(session.session_id),
        "fullname": user.fullname,
        "email": user.email,
        "exp": access_token_expires_at,
    }
    token = encode(jwt_payload)

    response.set_cookie(
        "access_token",
        token,
        expires=access_token_expires_at,
        samesite="lax",
        secure=cookie_is_secure,
        domain=cookie_domain
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        expires=refresh_token_expires_at,
        httponly=True,
        samesite="lax",
        secure=cookie_is_secure,
        domain=cookie_domain
    )

    try:
        session_data = SessionUserSchema.model_validate(session).model_dump_json()
        await redis.set(f"onyx:session:{session.session_id}", session_data, ex=ACCESS_TOKEN_EXP)
    except Exception as err:
        logger.warning(f"Failed to cache session in Redis for user {email}: {err}")

    try:
        arq = await get_arq_pool()
        await arq.enqueue_job("update_session", str(session.session_id), user_agent, _queue_name="onyx")
    except Exception as err:
        logger.warning(f"Failed to enqueue update_session background job: {err}")

    return {"success": True, "token": token, "refresh_token": refresh_token}

@router.post("/refresh_token")
@router.post("/refresh-token")
@limiter.limit("50/hour", error_message="Too many requests, try again later")
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    
    r_token_hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    stmt = (
        select(SessionModel)
        .options(
            selectinload(SessionModel.user)
            .selectinload(UserModel.current_subscription)
        )
        .where(SessionModel.refresh_token == r_token_hashed)
    )
    session = await db.scalar(stmt)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if not session or session.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired session",
        )

    new_refresh_token = secrets.token_urlsafe(30)
    n_r_hashed = hashlib.sha256(new_refresh_token.encode()).hexdigest()

    now_tz = datetime.now(timezone.utc)
    access_token_expires_at = now_tz + timedelta(seconds=ACCESS_TOKEN_EXP)
    refresh_token_expires_at = now_tz + timedelta(days=REFRESH_TOKEN_EXP)

    session.refresh_token = n_r_hashed
    session.expires_at = refresh_token_expires_at.replace(tzinfo=None)
    await db.commit()

    jwt_payload = {
        "sub": str(session.user.user_id),
        "session_id": str(session.session_id),
        "fullname": session.user.fullname,
        "email": session.user.email,
        "exp": access_token_expires_at,
    }

    token = encode(jwt_payload)

    response.set_cookie(
        "access_token",
        token,
        expires=access_token_expires_at,
        samesite="lax",
        secure=cookie_is_secure,
        domain=cookie_domain
    )
    response.set_cookie(
        "refresh_token",
        new_refresh_token,
        expires=refresh_token_expires_at,
        httponly=True,
        samesite="lax",
        secure=cookie_is_secure,
        domain=cookie_domain
    )

    try:
        session_data = SessionUserSchema.model_validate(session).model_dump_json()
        await redis.set(f"onyx:session:{session.session_id}", session_data, ex=ACCESS_TOKEN_EXP)
    except Exception as err:
        logger.warning(f"Failed to update session in Redis on refresh: {err}")

    return {"success": True, "token": token, "refresh_token": new_refresh_token}

@router.post("/signout")
@router.post("/logout")
async def signout(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
):
    if refresh_token:
        try:
            r_token_hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
            session = await db.scalar(
                select(SessionModel).where(SessionModel.refresh_token == r_token_hashed)
            )
            if session:
                await redis.delete(f"onyx:session:{session.session_id}")
                await db.delete(session)
                await db.commit()
        except Exception as err:
            logger.warning(f"Error during signout session deletion: {err}")

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"success": True}

@router.post("/change-password")
@limiter.limit("20/hour", error_message="Too many attempts, try again later")
async def change_password(
    request: Request,
    body: ChangePassIn,
    current_user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(
        select(UserModel)
        .options(selectinload(UserModel.sessions))
        .where(UserModel.user_id == current_user.user_id)
    )
    if not user or not password_hash.verify(body.current, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect password",
        )

    user.password = password_hash.hash(body.new_password)
    user.sessions.clear()
    await db.commit()
    return {"success": True}

@router.post("/send-reset-link")
@limiter.limit("5/minute", error_message="Too many requests, try again later")
async def send_reset_link(
    request: Request,
    body: ResetLinkIn,
    x_forwarded_for: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
):
    email = body.email.lower()
    user = await db.scalar(
        select(UserModel).where(func.lower(UserModel.email) == email)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist",
        )

    key_url = secrets.token_urlsafe(8)
    long_url = secrets.token_urlsafe(32)
    reset_token = f"{key_url}-onyx-{long_url}"
    payload = json.dumps({"email": email, "key": long_url})
    
    client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else (request.client.host if request.client else "127.0.0.1")
    await redis.set(f"onyx:passwordReset:{client_ip}:{key_url}", payload, ex=3600)
    
    return {"success": True, "reset_token": reset_token}

@router.get("/verify-reset-token")
@router.get("/validate-reset-link")
async def verify_reset_token(
    request: Request,
    token: str,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    parts = token.split("-onyx-")
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token format",
        )
    key_url, long_url = parts[0], parts[1]
    client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else (request.client.host if request.client else "127.0.0.1")

    result = await redis.get(f"onyx:passwordReset:{client_ip}:{key_url}")
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired or invalid reset token",
        )

    data = json.loads(result)
    if data.get("key") != long_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token key",
        )

    return {"success": True}

@router.post("/reset-password")
async def reset_password(
    request: Request,
    body: ResetPassIn,
    x_forwarded_for: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
):
    parts = body.token.split("-onyx-")
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token format",
        )
    key_url, long_url = parts[0], parts[1]
    client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else (request.client.host if request.client else "127.0.0.1")

    result = await redis.get(f"onyx:passwordReset:{client_ip}:{key_url}")
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired or invalid reset token",
        )

    data = json.loads(result)
    if data.get("key") != long_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    email = data["email"]
    hashed_password = password_hash.hash(body.new_password)

    await db.execute(
        update(UserModel)
        .where(UserModel.email == email)
        .values(password=hashed_password)
    )
    await db.commit()
    await redis.delete(f"onyx:passwordReset:{client_ip}:{key_url}")
    return {"success": True}
