import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import get_db
from models.admin import Tier as TierModel
from models.user import User as UserModel, Subscription as SubscriptionModel
from schemas.user import UserOut, SUBSCRIPTION_STATUS
from schemas.admin import SubscribeIn
from libs.deps import get_user
from libs.redis import redis
from libs.logger import logger
from payment import paystack
from workers.config import get_arq_pool

router = APIRouter()

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
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    now = datetime.now(timezone.utc)

    # If subscription tier price is 0 (Free Tier), activate directly without Paystack checkout
    if int(tier.price) < 1:
        new_sub = SubscriptionModel(
            user_id=user.user_id,
            amount=0,
            status=SUBSCRIPTION_STATUS.ACTIVE,
            idompotent_key=uuid.uuid4(),
            tier_id=tier.tier_id,
            expired_at=now + timedelta(days=3650),
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
        except Exception as err:
            logger.error(f"Failed to clear Redis session cache for user {user.user_id}: {err}")

        return {
            "success": True,
            "message": f"Successfully subscribed to {tier.name} free tier",
            "tier": tier.name,
            "subscription_id": new_sub.sub_id,
        }

    # For paid tiers: ensure Paystack customer exists
    if not user_obj.paystack_customer_id:
        try:
            arq = await get_arq_pool()
            await arq.enqueue_job("create_paystack_customer_task", str(user.user_id), user.email, user.fullname, _queue_name="onyx")
        except Exception as err:
            logger.warning(f"Failed to enqueue create_paystack_customer_task for user {user.email}: {err}")

    plan_code = tier.paystack_plan_code
    if not plan_code:
        plan_res = await paystack.create_subscription_plan(
            name=tier.name,
            amount_naira=tier.price,
            description=tier.description or f"Plan for {tier.name}",
        )
        if plan_res.get("status") and "data" in plan_res:
            plan_code = plan_res["data"].get("plan_code")
            tier.paystack_plan_code = plan_code
            await db.commit()

    metadata = {
        "user_id": str(user.user_id),
        "tier_id": str(tier.tier_id),
        "plan_code": plan_code,
    }

    tx_res = await paystack.initialize_transaction(
        email=user.email,
        amount_naira=tier.price,
        plan_code=plan_code,
        callback_url=body.callback_url,
        metadata=metadata,
    )

    if not tx_res.get("status") or "data" not in tx_res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize Paystack subscription payment: {tx_res.get('message', 'Unknown error')}",
        )

    data = tx_res["data"]
    return {
        "success": True,
        "authorization_url": data.get("authorization_url"),
        "access_code": data.get("access_code"),
        "reference": data.get("reference"),
        "tier": tier.name,
    }

@router.post("/verify-payment")
async def verify_payment(
    reference: str,
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    res = await paystack.verify_transaction(reference)
    if not res.get("status") or "data" not in res:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment verification failed")

    data = res["data"]
    if data.get("status") != "success":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment was not successful")

    metadata = data.get("metadata") or {}
    tier_id_str = metadata.get("tier_id")
    if not tier_id_str:
        return {"success": True, "message": "Payment verified"}

    tier = await db.scalar(select(TierModel).where(TierModel.tier_id == uuid.UUID(tier_id_str)))
    if not tier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found")

    user_obj = await db.scalar(select(UserModel).where(UserModel.user_id == user.user_id))
    amount = float(data.get("amount", 0)) / 100.0
    sub_code = data.get("subscription_code")
    authorization = data.get("authorization") or {}
    email_token = authorization.get("email_token")

    now = datetime.now(timezone.utc)
    new_sub = SubscriptionModel(
        user_id=user.user_id,
        amount=amount,
        status=SUBSCRIPTION_STATUS.ACTIVE,
        idompotent_key=uuid.uuid4(),
        tier_id=tier.tier_id,
        paystack_subscription_code=sub_code,
        paystack_email_token=email_token,
        expired_at=now + timedelta(days=30),
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
    except Exception as err:
        logger.error(f"Failed to clear Redis session cache for user {user.user_id}: {err}")

    return {"success": True, "message": "Payment verified and subscription activated", "tier": tier.name}

@router.get("/tiers")
async def list_tiers(db: AsyncSession = Depends(get_db)):
    tiers = await db.scalars(
        select(TierModel).where(TierModel.is_active == True, TierModel.deleted == False)
    )
    return tiers.all()

@router.post("/cancel")
async def cancel_subscription(
    user: UserOut = Depends(get_user),
    db: AsyncSession = Depends(get_db),
):
    user_obj = await db.scalar(
        select(UserModel)
        .options(selectinload(UserModel.current_subscription))
        .where(UserModel.user_id == user.user_id)
    )
    if not user_obj or not user_obj.current_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found")

    sub = user_obj.current_subscription
    if sub.paystack_subscription_code and sub.paystack_email_token:
        try:
            await paystack.disable_subscription(sub.paystack_subscription_code, sub.paystack_email_token)
        except Exception as err:
            logger.warning(f"Paystack disable_subscription failed: {err}")

    sub.status = SUBSCRIPTION_STATUS.CANCELLED
    await db.commit()

    try:
        keys = await redis.keys("onyx:session:*")
        for k in keys:
            raw = await redis.get(k)
            if raw and str(user.user_id) in raw.decode():
                await redis.delete(k)
    except Exception as err:
        logger.error(f"Failed to clear Redis session cache on sub cancel: {err}")

    return {"success": True, "message": "Subscription cancelled successfully"}

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
