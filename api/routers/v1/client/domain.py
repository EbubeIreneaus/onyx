import secrets
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, func, not_
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.redirect import Domain as DomainModel, Redirect as RedirectModel
from schemas.user import UserOut
from schemas.domain import DomainCreate, DomainUpdate, DomainResponse, DomainCheckRequest, DomainCheckResponse
from libs.deps import get_user
from libs.redis import redis
from permission import AppPermission
from setting import settings
from .utils import get_user_permissions_and_limits

router = APIRouter()

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

    permissions, limits = get_user_permissions_and_limits(user)
    is_subdomain = domain_name.endswith(settings.DOMAIN_NAME)

    if is_subdomain:
        if AppPermission.ONYX_SUBDOMAIN not in permissions and AppPermission.ONYX_SUBDOMAIN.value not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription tier does not allow Onyx subdomain creation",
            )

        existing_onyx_count = await db.scalar(
            select(func.count(DomainModel.id)).where(
                DomainModel.user_id == user.user_id,
                DomainModel.name.like(f"%.{settings.DOMAIN_NAME}"),
            )
        ) or 0

        if existing_onyx_count >= limits["max_onyx_subdomains"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Maximum Onyx subdomains limit ({limits['max_onyx_subdomains']}) reached for your tier",
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
        if AppPermission.CUSTOM_DOMAIN not in permissions and AppPermission.CUSTOM_DOMAIN.value not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription tier does not allow custom domain creation",
            )

        existing_custom_count = await db.scalar(
            select(func.count(DomainModel.id)).where(
                DomainModel.user_id == user.user_id,
                not_(DomainModel.name.like(f"%.{settings.DOMAIN_NAME}")),
            )
        ) or 0

        if existing_custom_count >= limits["max_custom_domains"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Maximum custom domains limit ({limits['max_custom_domains']}) reached for your tier",
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
