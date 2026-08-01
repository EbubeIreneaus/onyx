from schemas.user import UserManage
import secrets
import json
import uuid
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.redirect import Domain as DomainModel, Redirect as RedirectModel, RedirectVisitors as RedirectVisitorModel
from models.admin import Tier as TierModel
from models.user import User as UserModel, Subscription as SubscriptionModel
from schemas.user import UserOut, SUBSCRIPTION_STATUS
from schemas.domain import DomainCreate, DomainUpdate, DomainResponse, DomainCheckRequest, DomainCheckResponse
from schemas.redirect import RedirectCreate, RedirectUpdate, RedirectResponse, RedirectVisitorResponse
from schemas.admin import SubscribeIn
from libs.deps import get_user
from libs.redis import redis
from permission import AppPermission
from setting import settings

router = APIRouter(prefix="/client", tags=["Client"])

def get_user_permissions_and_limit(user: UserManage):
    if user.current_subscription and user.current_subscription.tier:
        raw_perms = user.current_subscription.tier.permissions or []
        permissions = set()
        for p in raw_perms:
            val = p.value if hasattr(p, "value") else str(p)
            permissions.add(val)
            permissions.add(p)
            try:
                permissions.add(AppPermission(val))
            except Exception:
                pass
        max_links = user.current_subscription.tier.max_short_link
    else:
        permissions = set()
        max_links = settings.MIN_ALLOWED_SHORT_LINKS
    return permissions, max_links

@router.post("/create-domain", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(
    body: DomainCreate,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    domain_name = body.name.lower().strip()
    if not domain_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Domain name is required")

    existing = await db.scalar(select(DomainModel).where(DomainModel.name == domain_name))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Domain already registered")

    permissions, _ = get_user_permissions_and_limit(user)
    is_subdomain = domain_name.endswith(settings.DOMAIN_NAME)

    if is_subdomain:
        if AppPermission.USE_ONYX_SUBDOMAIN not in permissions and AppPermission.USE_ONYX_SUBDOMAIN.value not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription tier does not allow Onyx subdomain creation",
            )
        new_domain = DomainModel(
            name=domain_name,
            user_id=user.user_id,
            txt_verified=True,
            cname_verified=True,
        )
        db.add(new_domain)
        await db.commit()
        await db.refresh(new_domain)
        return new_domain

    else:
        if AppPermission.CREATE_CUSTOM_DOMAIN not in permissions and AppPermission.CREATE_CUSTOM_DOMAIN.value not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription tier does not allow custom domain creation",
            )
        txt_token = f"onyx-verify-{secrets.token_hex(16)}"
        redis_key = f"onyx:txt_dns_verify:{user.user_id}:{domain_name}"
        await redis.set(redis_key, txt_token, ex=86400)

        new_domain = DomainModel(
            name=domain_name,
            user_id=user.user_id,
            txt_verified=False,
            cname_verified=False,
        )
        db.add(new_domain)
        await db.commit()
        await db.refresh(new_domain)
        return new_domain

@router.post("/check-domain", response_model=DomainCheckResponse)
async def check_domain(
    body: DomainCheckRequest,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    domain_name = body.domain.lower().strip()
    slug = body.slug.strip() if body.slug else ""

    if slug == "" and domain_name == settings.DOMAIN_NAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Root domain cannot be the main application domain",
        )

    domain_obj = await db.scalar(select(DomainModel).where(DomainModel.name == domain_name))

    is_subdomain = domain_name.endswith(settings.DOMAIN_NAME)
    txt_verification_token = None

    if not is_subdomain:
        redis_key = f"onyx:txt_dns_verify:{user.user_id}:{domain_name}"
        stored_token = await redis.get(redis_key)
        if stored_token:
            txt_verification_token = stored_token.decode() if isinstance(stored_token, bytes) else stored_token
            if domain_obj and not domain_obj.txt_verified:
                domain_obj.txt_verified = True
                await db.commit()

    existing_redirect = await db.scalar(
        select(RedirectModel).where(
            RedirectModel.domain == domain_name,
            RedirectModel.slug == (slug if slug != "" else None)
        )
    )

    if existing_redirect:
        return DomainCheckResponse(
            available=False,
            txt_verified=domain_obj.txt_verified if domain_obj else False,
            cname_verified=domain_obj.cname_verified if domain_obj else False,
            message="A short link with this domain and slug already exists",
            txt_verification_token=txt_verification_token
        )

    return DomainCheckResponse(
        available=True,
        txt_verified=domain_obj.txt_verified if domain_obj else is_subdomain,
        cname_verified=domain_obj.cname_verified if domain_obj else is_subdomain,
        message="Domain and slug path are available",
        txt_verification_token=txt_verification_token
    )

@router.get("/domains", response_model=List[DomainResponse])
async def list_domains(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    domains = await db.scalars(select(DomainModel).where(DomainModel.user_id == user.user_id))
    return domains.all()

@router.patch("/domains/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: int,
    body: DomainUpdate,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    domain_obj = await db.scalar(
        select(DomainModel).where(DomainModel.id == domain_id, DomainModel.user_id == user.user_id)
    )
    if not domain_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    if domain_obj.txt_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify a verified domain",
        )

    if body.name:
        new_name = body.name.lower().strip()
        existing = await db.scalar(select(DomainModel).where(DomainModel.name == new_name, DomainModel.id != domain_id))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Domain name already taken")
        domain_obj.name = new_name

    await db.commit()
    await db.refresh(domain_obj)
    return domain_obj

@router.delete("/domains/{domain_id}")
async def delete_domain(
    domain_id: int,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    domain_obj = await db.scalar(
        select(DomainModel).where(DomainModel.id == domain_id, DomainModel.user_id == user.user_id)
    )
    if not domain_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    await db.delete(domain_obj)
    await db.commit()
    return {"success": True, "detail": "Domain deleted successfully"}

@router.post("/create-short", response_model=RedirectResponse, status_code=status.HTTP_201_CREATED)
async def create_short_link(
    body: RedirectCreate,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    permissions, max_links = get_user_permissions_and_limit(user)

    target_domain = body.domain.lower().strip() if body.domain else settings.DOMAIN_NAME

    if target_domain != settings.DOMAIN_NAME:
        is_subdomain = target_domain.endswith(settings.DOMAIN_NAME)
        if is_subdomain:
            if AppPermission.USE_ONYX_SUBDOMAIN not in permissions and AppPermission.USE_ONYX_SUBDOMAIN.value not in permissions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Subdomain permissions required")
        else:
            if AppPermission.CREATE_CUSTOM_DOMAIN not in permissions and AppPermission.CREATE_CUSTOM_DOMAIN.value not in permissions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Custom domain permissions required")

    active_count = await db.scalar(
        select(func.count(RedirectModel.id)).where(RedirectModel.user_id == user.user_id, RedirectModel.expired == False)
    )
    if active_count >= max_links:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Maximum short link limit ({max_links}) reached for your tier",
        )

    if body.slug:
        if AppPermission.USE_CUSTOM_PATH not in permissions and AppPermission.USE_CUSTOM_PATH.value not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Custom path/slug permission required",
            )
        slug = body.slug.strip()
        existing_slug = await db.scalar(
            select(RedirectModel).where(RedirectModel.domain == target_domain, RedirectModel.slug == slug)
        )
        if existing_slug:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already in use for this domain")
    else:
        slug = secrets.token_urlsafe(4)[:6]

    new_redirect = RedirectModel(
        user_id=user.user_id,
        domain=target_domain,
        slug=slug,
        destination=body.destination,
        expired_on=body.expired_on,
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
        permissions, _ = get_user_permissions_and_limit(user)
        if AppPermission.USE_CUSTOM_PATH not in permissions and AppPermission.USE_CUSTOM_PATH.value not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Custom slug permission required")
        existing_slug = await db.scalar(
            select(RedirectModel).where(RedirectModel.domain == r.domain, RedirectModel.slug == body.slug, RedirectModel.id != r.id)
        )
        if existing_slug:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already in use")
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

@router.post("/subscribe")
async def subscribe_tier(
    body: SubscribeIn,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    tier = await db.scalar(select(TierModel).where(TierModel.tier_id == body.tier_id, TierModel.is_active == True))
    if not tier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription tier not found")

    user_obj = await db.scalar(select(UserModel).where(UserModel.user_id == user.user_id))
    idempotent_key = secrets.token_bytes(16)
    
    new_sub = SubscriptionModel(
        user_id=user.user_id,
        amount=tier.price,
        status=SUBSCRIPTION_STATUS.ACTIVE,
        idompotent_key=uuid.uuid4(),
        tier_id=tier.tier_id,
        expired_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(new_sub)
    await db.flush()

    user_obj.current_sub_id = new_sub.sub_id
    await db.commit()

    try:
        keys = await redis.keys("onyx:session:*")
        for k in keys:
            raw = await redis.get(k)
            if raw and str(user.user_id) in raw.decode():
                await redis.delete(k)
    except Exception:
        pass

    return {"success": True, "subscription_id": new_sub.sub_id, "tier": tier.name}

@router.get("/subscription")
async def get_subscription(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    user_obj = await db.scalar(
        select(UserModel)
        .options(selectinload(UserModel.current_subscription).selectinload(SubscriptionModel.tier))
        .where(UserModel.user_id == user.user_id)
    )
    return {"subscription": user_obj.current_subscription if user_obj else None}
