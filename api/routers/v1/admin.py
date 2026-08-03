from sqlalchemy import func
from permission import AdminPermission
from schemas.user import UserManage
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.admin import Tier as TierModel
from schemas.admin import TierCreate, TierUpdate, TierResponse
from schemas.user import UserOut
from libs.deps import get_admin
from libs.logger import logger
from libs.redis import redis
from workers.config import get_arq_pool

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/tiers", response_model=TierResponse, status_code=status.HTTP_201_CREATED)
async def create_tier(
    body: TierCreate,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    if not admin.admin_priviledges or (
        AdminPermission.MANAGE_TIERS not in admin.admin_priviledges
        and AdminPermission.MANAGE_ALL not in admin.admin_priviledges
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a subscription tier",
        )

    tier_name = body.name.lower().strip().split(" ")[0]
    existing = await db.scalar(select(TierModel).where(func.lower(TierModel.name) == tier_name))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subscription tier with this name already exists",
        )

    perm_strings = [
        p.value if hasattr(p, "value") else str(p) for p in body.permissions
    ]

    new_tier = TierModel(
        **body.model_dump(exclude_unset=True, exclude_none=True, exclude={"permissions", "name"}),
        permissions=perm_strings,
        name=tier_name
    )

    db.add(new_tier)
    await db.commit()
    await db.refresh(new_tier)

    if int(new_tier.price) > 0:
        try:
            arq = await get_arq_pool()
            await arq.enqueue_job("sync_paystack_plan_task", str(new_tier.tier_id), _queue_name="onyx")
        except Exception as err:
            logger.warning(f"Failed to enqueue sync_paystack_plan_task for new tier {new_tier.tier_id - new_tier.name}: {err}")

    try:
        await redis.delete("onyx:pricings")
    except Exception as err:
        logger.warning(f"Failed to clear onyx:pricings Redis cache: {err}")

    return new_tier


@router.get("/tiers", response_model=List[TierResponse])
async def list_tiers(
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    tiers = await db.scalars(select(TierModel))
    return tiers.all()


@router.get("/tiers/{tier_id}", response_model=TierResponse)
async def get_tier(
    tier_id: uuid.UUID,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    tier = await db.scalar(select(TierModel).where(TierModel.tier_id == tier_id))
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found"
        )
    return tier


@router.patch("/tiers/{tier_id}", response_model=TierResponse)
async def update_tier(
    tier_id: uuid.UUID,
    body: TierUpdate,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    if not admin.admin_priviledges or (
        AdminPermission.MANAGE_TIERS not in admin.admin_priviledges
        and AdminPermission.MANAGE_ALL not in admin.admin_priviledges
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a subscription tier",
        )

    tier = await db.scalar(select(TierModel).where(TierModel.tier_id == tier_id))
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found"
        )

    if body.name is not None:
        existing = await db.scalar(
            select(TierModel).where(
                TierModel.name == body.name, TierModel.tier_id != tier_id
            )
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Tier name already in use"
            )
        tier.name = body.name
    if body.price is not None:
        tier.price = body.price
    if body.permissions is not None:
        tier.permissions = [
            p.value if hasattr(p, "value") else str(p) for p in body.permissions
        ]
    if body.max_short_link is not None:
        tier.max_short_link = body.max_short_link
    if body.is_active is not None:
        tier.is_active = body.is_active

    await db.commit()
    await db.refresh(tier)

    try:
        arq = await get_arq_pool()
        await arq.enqueue_job("sync_paystack_plan_task", str(tier.tier_id), _queue_name="onyx")
    except Exception as err:
        logger.warning(f"Failed to enqueue sync_paystack_plan_task for tier {tier.tier_id}: {err}")

    try:
        await redis.delete("onyx:pricings")
    except Exception as err:
        logger.warning(f"Failed to clear onyx:pricings Redis cache: {err}")

    return tier


@router.delete("/tiers/{tier_id}")
async def delete_tier(
    tier_id: uuid.UUID,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):

    if not admin.admin_priviledges or (
        AdminPermission.MANAGE_TIERS not in admin.admin_priviledges
        and AdminPermission.MANAGE_ALL not in admin.admin_priviledges
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete a subscription tier",
        )

    tier = await db.scalar(select(TierModel).where(TierModel.tier_id == tier_id))
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found"
        )

    await db.delete(tier)
    await db.commit()

    try:
        await redis.delete("onyx:pricings")
    except Exception as err:
        logger.warning(f"Failed to clear onyx:pricings Redis cache: {err}")

    return {"success": True, "detail": "Tier deleted successfully"}


# ─────────────────────────────────────────────────────────────────────────────
# Platform Overview Analytics
# ─────────────────────────────────────────────────────────────────────────────

from models.user import User as UserModel, Subscription as SubModel
from models.redirect import Redirect as RedirectModel, Domain as DomainModel, RedirectVisitors
from schemas.admin import (
    AdminAnalyticsResponse,
    AdminUserListItem,
    AdminDomainListItem,
    AdminRedirectListItem,
    UserStatusUpdate,
    UserRoleUpdate,
    UserTierUpdate,
)
from schemas.user import USER_STATUS

@router.get("/analytics", response_model=AdminAnalyticsResponse)
async def get_admin_analytics(
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    total_users = (await db.scalar(select(func.count(UserModel.id)).where(UserModel.deleted_at.is_(None)))) or 0
    active_users = (await db.scalar(select(func.count(UserModel.id)).where(UserModel.status == USER_STATUS.ACTIVE, UserModel.deleted_at.is_(None)))) or 0
    suspended_users = (await db.scalar(select(func.count(UserModel.id)).where(UserModel.status == USER_STATUS.SUSPENDED, UserModel.deleted_at.is_(None)))) or 0

    total_redirects = (await db.scalar(select(func.count(RedirectModel.id)))) or 0
    total_visits = (await db.scalar(select(func.count(RedirectVisitors.id)))) or 0

    total_domains = (await db.scalar(select(func.count(DomainModel.id)))) or 0
    verified_domains = (await db.scalar(select(func.count(DomainModel.id)).where(DomainModel.txt_verified.is_(True) | DomainModel.cname_verified.is_(True)))) or 0

    active_tiers_count = (await db.scalar(select(func.count(TierModel.id)).where(TierModel.is_active.is_(True)))) or 0

    return AdminAnalyticsResponse(
        total_users=total_users,
        active_users=active_users,
        suspended_users=suspended_users,
        total_redirects=total_redirects,
        total_visits=total_visits,
        total_domains=total_domains,
        verified_domains=verified_domains,
        active_tiers_count=active_tiers_count,
    )


# ─────────────────────────────────────────────────────────────────────────────
# User Management
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=List[AdminUserListItem])
async def list_admin_users(
    search: str | None = None,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(UserModel)
        .options(
            selectinload(UserModel.current_subscription).selectinload(SubModel.tier),
            selectinload(UserModel.redirects),
            selectinload(UserModel.domains),
        )
        .where(UserModel.deleted_at.is_(None))
        .order_by(UserModel.created_at.desc())
    )

    if search:
        search_clean = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            func.lower(UserModel.email).like(search_clean) |
            func.lower(UserModel.fullname).like(search_clean)
        )

    users_raw = (await db.scalars(stmt)).all()
    results = []
    for u in users_raw:
        tier_name = u.current_subscription.tier.name if (u.current_subscription and u.current_subscription.tier) else "Free / No Tier"
        results.append(
            AdminUserListItem(
                id=u.id,
                user_id=u.user_id,
                fullname=u.fullname,
                email=u.email,
                is_admin=u.is_admin or False,
                status=u.status.value if hasattr(u.status, "value") else str(u.status),
                tier_name=tier_name,
                created_at=u.created_at,
                redirects_count=len(u.redirects or []),
                domains_count=len(u.domains or []),
            )
        )
    return results


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: uuid.UUID,
    body: UserStatusUpdate,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    target = await db.scalar(select(UserModel).where(UserModel.user_id == user_id, UserModel.deleted_at.is_(None)))
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_status = body.status.upper().strip()
    if new_status == "ACTIVE":
        target.status = USER_STATUS.ACTIVE
    elif new_status == "SUSPENDED":
        target.status = USER_STATUS.SUSPENDED
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value. Use ACTIVE or SUSPENDED")

    await db.commit()
    return {"success": True, "message": f"User status updated to {new_status}"}


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: uuid.UUID,
    body: UserRoleUpdate,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    target = await db.scalar(select(UserModel).where(UserModel.user_id == user_id, UserModel.deleted_at.is_(None)))
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    target.is_admin = body.is_admin
    if body.admin_privileges is not None:
        target.admin_priviledges = body.admin_privileges
    await db.commit()
    return {"success": True, "message": "User admin roles updated successfully"}


# ─────────────────────────────────────────────────────────────────────────────
# Domain Management & Force Verify
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/domains", response_model=List[AdminDomainListItem])
async def list_admin_domains(
    search: str | None = None,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(DomainModel)
        .options(selectinload(DomainModel.user))
        .order_by(DomainModel.created_at.desc())
    )

    if search:
        search_clean = f"%{search.strip().lower()}%"
        stmt = stmt.where(func.lower(DomainModel.name).like(search_clean))

    domains_raw = (await db.scalars(stmt)).all()
    results = []
    for d in domains_raw:
        results.append(
            AdminDomainListItem(
                id=d.id,
                name=d.name,
                user_email=d.user.email if d.user else "Unknown",
                txt_verified=d.txt_verified,
                cname_verified=d.cname_verified,
                is_root_domain=d.is_root_domain,
                created_at=d.created_at,
            )
        )
    return results


@router.post("/domains/{domain_id}/force-verify")
async def force_verify_domain(
    domain_id: int,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    domain_obj = await db.scalar(select(DomainModel).where(DomainModel.id == domain_id))
    if not domain_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    domain_obj.txt_verified = True
    domain_obj.cname_verified = True
    await db.commit()
    return {"success": True, "message": f"Domain '{domain_obj.name}' force-verified successfully!"}


@router.delete("/domains/{domain_id}")
async def delete_admin_domain(
    domain_id: int,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    domain_obj = await db.scalar(select(DomainModel).where(DomainModel.id == domain_id))
    if not domain_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    await db.delete(domain_obj)
    await db.commit()
    return {"success": True, "message": "Domain deleted successfully"}


# ─────────────────────────────────────────────────────────────────────────────
# Redirects & Short Links Management
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/redirects", response_model=List[AdminRedirectListItem])
async def list_admin_redirects(
    search: str | None = None,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(RedirectModel)
        .options(selectinload(RedirectModel.user), selectinload(RedirectModel.visitors))
        .order_by(RedirectModel.created_at.desc())
    )

    if search:
        search_clean = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            func.lower(RedirectModel.slug).like(search_clean) |
            func.lower(RedirectModel.domain).like(search_clean) |
            func.lower(RedirectModel.destination).like(search_clean)
        )

    redirects_raw = (await db.scalars(stmt)).all()
    results = []
    for r in redirects_raw:
        results.append(
            AdminRedirectListItem(
                id=r.redirect_id,
                domain=r.domain,
                slug=r.slug,
                destination=r.destination,
                visits=len(r.visitors or []),
                expired=r.expired,
                user_email=r.user.email if r.user else "Unknown",
                created_at=r.created_at,
            )
        )
    return results


@router.patch("/redirects/{redirect_id}/status")
async def update_admin_redirect_status(
    redirect_id: uuid.UUID,
    expired: bool,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    r = await db.scalar(select(RedirectModel).where(RedirectModel.redirect_id == redirect_id))
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redirect not found")

    r.expired = expired
    await db.commit()
    return {"success": True, "message": f"Link status updated (expired={expired})"}


@router.delete("/redirects/{redirect_id}")
async def delete_admin_redirect(
    redirect_id: uuid.UUID,
    admin: UserManage = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    r = await db.scalar(select(RedirectModel).where(RedirectModel.redirect_id == redirect_id))
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redirect not found")

    await db.delete(r)
    await db.commit()
    return {"success": True, "message": "Redirect deleted successfully"}

