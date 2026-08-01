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

        if not domain_obj.txt_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain TXT record verification must be completed before creating short links",
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
    max_expired_on = datetime.now(timezone.utc) + timedelta(days=durability_days)

    if body.expired_on:
        req_expired = body.expired_on if body.expired_on.tzinfo else body.expired_on.replace(tzinfo=timezone.utc)
        expired_on = min(req_expired, max_expired_on)
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
