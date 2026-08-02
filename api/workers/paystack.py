import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.db import SessionLocal
from models.user import User as UserModel, Subscription as SubscriptionModel
from models.admin import Tier as TierModel
from schemas.user import SUBSCRIPTION_STATUS
from payment import paystack
from libs.redis import redis
from libs.logger import logger

async def create_paystack_customer_task(ctx: dict, user_id_str: str, email: str, fullname: str):
    names = fullname.strip().split(" ", 1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else ""

    res = await paystack.create_customer(email=email, first_name=first_name, last_name=last_name)
    if res.get("status") and "data" in res:
        customer_code = res["data"].get("customer_code") or str(res["data"].get("id"))
        async with SessionLocal() as db:
            try:
                user_uuid = uuid.UUID(user_id_str)
                user = await db.scalar(select(UserModel).where(UserModel.user_id == user_uuid))
                if user:
                    user.paystack_customer_id = customer_code
                    await db.commit()
                    logger.info(f"Updated Paystack customer ID '{customer_code}' for user {user.email}")
            except Exception as e:
                await db.rollback()
                logger.exception(f"Error updating paystack_customer_id in DB: {e}")

async def sync_paystack_plan_task(ctx: dict, tier_id_str: str):
    async with SessionLocal() as db:
        try:
            tier_uuid = uuid.UUID(tier_id_str)
            tier = await db.scalar(select(TierModel).where(TierModel.tier_id == tier_uuid))
            if not tier:
                logger.error(f"Tier {tier_id_str} not found for Paystack plan sync")
                return

            if not tier.paystack_plan_code:
                res = await paystack.create_subscription_plan(
                    name=tier.name,
                    amount_naira=tier.price,
                    description=tier.description or f"Plan for {tier.name}",
                )
                if res.get("status") and "data" in res:
                    plan_code = res["data"].get("plan_code")
                    tier.paystack_plan_code = plan_code
                    await db.commit()
                    logger.info(f"Created Paystack plan '{plan_code}' for tier '{tier.name}'")
            else:
                res = await paystack.update_subscription_plan(
                    plan_code=tier.paystack_plan_code,
                    name=tier.name,
                    amount_naira=tier.price,
                    description=tier.description or f"Plan for {tier.name}",
                )
                logger.info(f"Updated Paystack plan '{tier.paystack_plan_code}' for tier '{tier.name}'")
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error syncing Paystack plan for tier {tier_id_str}: {e}")

async def process_paystack_webhook_task(ctx: dict, event_type: str, data: Dict[str, Any]):
    async with SessionLocal() as db:
        try:
            if event_type == "charge.success":
                customer_info = data.get("customer", {})
                customer_email = customer_info.get("email", "").lower()
                customer_code = customer_info.get("customer_code")
                amount = float(data.get("amount", 0)) / 100.0
                metadata = data.get("metadata") or {}
                plan_info = data.get("plan") or {}
                plan_code = plan_info.get("plan_code") or metadata.get("plan_code")
                sub_code = data.get("subscription_code")
                authorization = data.get("authorization") or {}
                email_token = authorization.get("email_token")

                user = None
                user_id_str = metadata.get("user_id")
                if user_id_str:
                    try:
                        user = await db.scalar(select(UserModel).where(UserModel.user_id == uuid.UUID(user_id_str)))
                    except Exception as err:
                        logger.warning(f"Error resolving user UUID '{user_id_str}': {err}")
                if not user and customer_email:
                    user = await db.scalar(select(UserModel).where(UserModel.email == customer_email))

                if not user:
                    logger.error(f"User not found for charge.success webhook (email: {customer_email})")
                    return

                if customer_code and not user.paystack_customer_id:
                    user.paystack_customer_id = customer_code

                tier = None
                tier_id_str = metadata.get("tier_id")
                if tier_id_str:
                    try:
                        tier = await db.scalar(select(TierModel).where(TierModel.tier_id == uuid.UUID(tier_id_str)))
                    except Exception as err:
                        logger.warning(f"Error resolving tier UUID '{tier_id_str}': {err}")
                        
                if not tier and plan_code:
                    tier = await db.scalar(select(TierModel).where(TierModel.paystack_plan_code == plan_code))

                if not tier:
                    logger.error(f"Tier not found for plan_code '{plan_code}'")
                    return

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

                user.current_sub_id = new_sub.sub_id
                await db.commit()

                # Clear session cache so permission updates take effect instantly
                try:
                    keys = await redis.keys("onyx:session:*")
                    for k in keys:
                        raw = await redis.get(k)
                        if raw and str(user.user_id) in raw.decode():
                            await redis.delete(k)
                except Exception as err:
                    logger.error(f"Failed to clear Redis session cache for user {user.user_id}: {err}")

                logger.info(f"Successfully activated subscription {new_sub.sub_id} for user {user.email}")

            elif event_type == "subscription.create":
                sub_code = data.get("subscription_code")
                email_token = data.get("email_token")
                customer_info = data.get("customer", {})
                customer_email = customer_info.get("email", "").lower()

                if customer_email:
                    user = await db.scalar(
                        select(UserModel)
                        .options(selectinload(UserModel.current_subscription))
                        .where(UserModel.email == customer_email)
                    )
                    if user and user.current_subscription:
                        user.current_subscription.paystack_subscription_code = sub_code
                        user.current_subscription.paystack_email_token = email_token
                        await db.commit()
                        logger.info(f"Updated subscription_code '{sub_code}' for user {user.email}")

            elif event_type in ("subscription.disable", "subscription.not_renew"):
                sub_code = data.get("subscription_code")
                if sub_code:
                    sub = await db.scalar(
                        select(SubscriptionModel).where(SubscriptionModel.paystack_subscription_code == sub_code)
                    )
                    if sub:
                        sub.status = SUBSCRIPTION_STATUS.CANCELLED
                        await db.commit()

                        try:
                            keys = await redis.keys("onyx:session:*")
                            for k in keys:
                                raw = await redis.get(k)
                                if raw and str(sub.user_id) in raw.decode():
                                    await redis.delete(k)
                        except Exception as err:
                            logger.error(f"Failed to clear Redis session cache for user {sub.user_id}: {err}")
                        logger.info(f"Cancelled subscription '{sub_code}' for user {sub.user_id}")
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error processing Paystack webhook event '{event_type}': {e}")
