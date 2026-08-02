import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.redirect import Domain as DomainModel, Redirect as RedirectModel, RedirectVisitors as RedirectVisitorModel
from schemas.user import UserOut
from schemas.redirect import RedirectCreate, RedirectUpdate, RedirectResponse, RedirectVisitorResponse
from libs.deps import get_user
from permission import AppPermission
from setting import settings
from .utils import get_user_permissions_and_limits

router = APIRouter()

@router.post("/create-short", response_model=RedirectResponse, status_code=status.HTTP_201_CREATED)
async def create_short_link(
    body: RedirectCreate,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    permissions, limits = get_user_permissions_and_limits(user)

    # 1. Require FREE_LINK permission to create any short link
    if AppPermission.FREE_LINK not in permissions and AppPermission.FREE_LINK.value not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your subscription tier does not permit short link creation",
        )

    # 2. Check total active short links quota
    active_count = await db.scalar(
        select(func.count(RedirectModel.id)).where(
            RedirectModel.user_id == user.user_id,
            RedirectModel.expired == False
        )
    ) or 0

    if active_count >= limits["max_short_link"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Maximum short link limit ({limits['max_short_link']}) reached for your tier",
        )

    target_domain = body.domain.lower().strip() if body.domain else settings.DOMAIN_NAME

    # 3. Domain ownership & TXT verification checks for non-default domains
    if target_domain != settings.DOMAIN_NAME:
        domain_obj = await db.scalar(select(DomainModel).where(DomainModel.name == target_domain))
        if not domain_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain must be registered and verified before creating short links",
            )

        if domain_obj.user_id != user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this domain",
            )

        if not (domain_obj.txt_verified or domain_obj.cname_verified):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain DNS verification must be completed before creating short links",
            )

        is_subdomain = target_domain.endswith(settings.DOMAIN_NAME)
        if is_subdomain:
            if AppPermission.ONYX_SUBDOMAIN not in permissions and AppPermission.ONYX_SUBDOMAIN.value not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Subscription tier does not allow Onyx subdomain links",
                )
        else:
            if AppPermission.CUSTOM_DOMAIN not in permissions and AppPermission.CUSTOM_DOMAIN.value not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Subscription tier does not allow custom domain links",
                )

    # 4. Custom path / slug permissions & limits check
    if body.slug:
        if AppPermission.CUSTOM_PATH not in permissions and AppPermission.CUSTOM_PATH.value not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Custom path/slug permission required",
            )

        custom_paths_count = await db.scalar(
            select(func.count(RedirectModel.id)).where(
                RedirectModel.user_id == user.user_id,
                RedirectModel.slug.is_not(None)
            )
        ) or 0

        if custom_paths_count >= limits["max_custom_paths"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Maximum custom paths limit ({limits['max_custom_paths']}) reached for your tier",
            )

        slug = body.slug.strip()
    else:
        slug = secrets.token_urlsafe(4)[:6]

    # 5. Unique constraint check for (domain, slug)
    existing_link = await db.scalar(
        select(RedirectModel).where(
            RedirectModel.domain == target_domain,
            RedirectModel.slug == slug,
        )
    )
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A short link with this domain and path/slug already exists",
        )

    durability_days = limits.get("link_durability", 14)
    is_unlimited_durability = (
        durability_days == "unlimited"
        or durability_days == "forever"
        or type(durability_days).__name__ == "UnlimitedLimit"
    )

    if is_unlimited_durability:
        max_expired_on = None
    else:
        try:
            days_int = int(durability_days)
            max_expired_on = datetime.now(timezone.utc) + timedelta(days=days_int)
        except Exception:
            max_expired_on = None

    if body.expired_on:
        req_expired = body.expired_on if body.expired_on.tzinfo else body.expired_on.replace(tzinfo=timezone.utc)
        if max_expired_on:
            expired_on = min(req_expired, max_expired_on)
        else:
            expired_on = req_expired
    else:
        expired_on = max_expired_on

    new_redirect = RedirectModel(
        user_id=user.user_id,
        domain=target_domain,
        slug=slug,
        destination=body.destination,
        expired_on=expired_on,
    )

    db.add(new_redirect)
    await db.commit()
    await db.refresh(new_redirect)
    return new_redirect

@router.get("/redirects", response_model=List[RedirectResponse])
async def list_redirects(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    redirects = await db.scalars(
        select(RedirectModel)
        .options(selectinload(RedirectModel.visitors))
        .where(RedirectModel.user_id == user.user_id)
    )
    results = []
    for r in redirects.all():
        item = RedirectResponse.model_validate(r)
        item.visitor_count = len(r.visitors)
        results.append(item)
    return results

@router.get("/redirects/{redirect_id}")
async def get_redirect(
    redirect_id: str,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RedirectModel).options(selectinload(RedirectModel.visitors)).where(
        RedirectModel.user_id == user.user_id
    )
    try:
        r_uuid = uuid.UUID(redirect_id)
        stmt = stmt.where(RedirectModel.redirect_id == r_uuid)
    except ValueError:
        stmt = stmt.where(RedirectModel.slug == redirect_id)

    r = await db.scalar(stmt)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redirect link not found")

    res = RedirectResponse.model_validate(r)
    res.visitor_count = len(r.visitors)
    visitors_data = [RedirectVisitorResponse.model_validate(v) for v in r.visitors]

    return {"redirect": res, "visitors": visitors_data}

@router.patch("/redirects/{redirect_id}", response_model=RedirectResponse)
async def update_redirect(
    redirect_id: str,
    body: RedirectUpdate,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RedirectModel).where(RedirectModel.user_id == user.user_id)
    try:
        r_uuid = uuid.UUID(redirect_id)
        stmt = stmt.where(RedirectModel.redirect_id == r_uuid)
    except ValueError:
        stmt = stmt.where(RedirectModel.slug == redirect_id)

    r = await db.scalar(stmt)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redirect not found")

    if body.destination:
        r.destination = body.destination
    if body.slug:
        permissions, _ = get_user_permissions_and_limits(user)
        if AppPermission.CUSTOM_PATH not in permissions and AppPermission.CUSTOM_PATH.value not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Custom slug permission required")
        existing_slug = await db.scalar(
            select(RedirectModel).where(RedirectModel.domain == r.domain, RedirectModel.slug == body.slug, RedirectModel.id != r.id)
        )
        if existing_slug:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A short link with this domain and slug already exists")
        r.slug = body.slug
    if body.expired is not None:
        r.expired = body.expired
    if body.expired_on is not None:
        r.expired_on = body.expired_on

    await db.commit()
    await db.refresh(r)
    return r

@router.delete("/redirects/{redirect_id}")
async def delete_redirect(
    redirect_id: str,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RedirectModel).where(RedirectModel.user_id == user.user_id)
    try:
        r_uuid = uuid.UUID(redirect_id)
        stmt = stmt.where(RedirectModel.redirect_id == r_uuid)
    except ValueError:
        stmt = stmt.where(RedirectModel.slug == redirect_id)

    r = await db.scalar(stmt)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redirect not found")

    await db.delete(r)
    await db.commit()
    return {"success": True, "detail": "Redirect deleted"}

import json
from typing import Annotated
from fastapi import Request, Header
from libs.redis import redis
from libs.logger import logger
from schemas.redirect import RedirectResolveRequest, RedirectResolveResponse
from models.user import User, Subscription

@router.post("/resolve-redirect", response_model=RedirectResolveResponse)
async def resolve_redirect(
    request: Request,
    body: RedirectResolveRequest,
    db: AsyncSession = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    from workers.config import get_arq_pool
    raw_domain = body.domain.lower().strip() if body.domain else ""
    slug = (body.slug or "").strip().lstrip('/')

    if body.full_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(body.full_url)
            if parsed.netloc:
                raw_domain = parsed.netloc.lower().split(':')[0]
            if not slug and parsed.path:
                slug = parsed.path.strip('/')
        except Exception:
            pass

    domain = raw_domain if raw_domain else settings.DOMAIN_NAME
    redis_key = f"onyx:redirect:{domain}:{slug}"

    client_ip = "127.0.0.1"
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0].strip()
    elif request.client:
        client_ip = request.client.host

    ua = user_agent or "Unknown"

    cached_data = None
    try:
        cached_raw = await redis.get(redis_key)
        if cached_raw:
            cached_data = json.loads(cached_raw)
    except Exception as err:
        logger.warning(f"Redis lookup error for redirect {redis_key}: {err}")

    now = datetime.now(timezone.utc)

    if cached_data:
        is_expired = cached_data.get("expired", False)
        exp_str = cached_data.get("expired_on")
        if exp_str:
            try:
                exp_dt = datetime.fromisoformat(exp_str)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                if exp_dt <= now:
                    is_expired = True
            except Exception:
                pass

        if is_expired:
            return RedirectResolveResponse(found=False, expired=True, message="Link has expired")

        redirect_id_str = cached_data.get("redirect_id")
        destination = cached_data.get("destination")

        if redirect_id_str:
            try:
                arq = await get_arq_pool()
                await arq.enqueue_job(
                    "log_redirect_visitor_task",
                    redirect_id_str,
                    client_ip,
                    ua,
                    _queue_name="onyx"
                )
            except Exception as err:
                logger.warning(f"Failed to enqueue visitor tracking job: {err}")

        return RedirectResolveResponse(found=True, destination=destination, expired=False)

    stmt = (
        select(RedirectModel)
        .options(selectinload(RedirectModel.user).selectinload(User.current_subscription).selectinload(Subscription.tier))
        .where(
            RedirectModel.domain == domain,
            RedirectModel.slug == slug,
        )
    )
    redirect_obj = await db.scalar(stmt)

    if not redirect_obj:
        return RedirectResolveResponse(found=False, expired=False, message="Short link not found")

    is_expired = redirect_obj.expired
    if redirect_obj.expired_on:
        exp_dt = redirect_obj.expired_on
        if exp_dt.tzinfo is None:
            exp_dt = exp_dt.replace(tzinfo=timezone.utc)
        if exp_dt <= now:
            is_expired = True
            redirect_obj.expired = True
            await db.commit()

    if is_expired:
        return RedirectResolveResponse(found=False, expired=True, message="Short link has expired")

    try:
        cache_payload = {
            "redirect_id": str(redirect_obj.redirect_id),
            "destination": redirect_obj.destination,
            "expired": redirect_obj.expired,
            "expired_on": redirect_obj.expired_on.isoformat() if redirect_obj.expired_on else None,
        }
        await redis.set(redis_key, json.dumps(cache_payload), ex=3600)
    except Exception as err:
        logger.warning(f"Failed to cache redirect in Redis: {err}")

    try:
        arq = await get_arq_pool()
        await arq.enqueue_job(
            "log_redirect_visitor_task",
            str(redirect_obj.redirect_id),
            client_ip,
            ua,
            _queue_name="onyx"
        )
    except Exception as err:
        logger.warning(f"Failed to enqueue visitor tracking job: {err}")

    return RedirectResolveResponse(found=True, destination=redirect_obj.destination, expired=False)
