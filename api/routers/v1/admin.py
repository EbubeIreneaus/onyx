from sqlalchemy import func
from permission import AdminPermission
from schemas.user import UserManage
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.admin import Tier as TierModel
from schemas.admin import TierCreate, TierUpdate, TierResponse
from schemas.user import UserOut
from libs.deps import get_admin

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
    return {"success": True, "detail": "Tier deleted successfully"}
