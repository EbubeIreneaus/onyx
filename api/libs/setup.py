from decimal import Decimal
from datetime import datetime, timedelta, timezone
import uuid
from pwdlib import PasswordHash
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.admin import Tier as TierModel
from models.user import User as UserModel, Subscription as SubscriptionModel
from permission import AdminPermission, AppPermission
from schemas.user import SUBSCRIPTION_STATUS
from setting import settings
from libs.logger import logger
from models.db import SessionLocal



async def ensure_default_admin_and_tier() -> None:
    async with SessionLocal() as session:
        admin_email = settings.ONYX_ADMIN_EMAIL
        existing_admin = await session.scalar(
            select(UserModel).where(UserModel.email == admin_email)
        )

        if not existing_admin:
            password_hasher = PasswordHash.recommended()
            password_hash = password_hasher.hash(settings.ONYX_ADMIN_PASS)
            admin_user = UserModel(
                fullname="Onyx Admin",
                email=admin_email,
                password=password_hash,
                is_admin=True,
                admin_priviledges=[AdminPermission.MANAGE_ALL.value],
                email_verified=True,
                status="ACTIVE",
            )
            session.add(admin_user)
            await session.flush()
            logger.info(f"Created default admin user {admin_email}")
        else:
            admin_user = existing_admin

        existing_tier = await session.scalar(
            select(TierModel).where(func.lower(TierModel.name) == "free")
        )

        if not existing_tier:
            free_tier = TierModel(
                name="free",
                description="Default free tier",
                price=Decimal("0.00"),
                permissions=[AppPermission.FREE_LINK.value],
                max_short_link=str(settings.MIN_ALLOWED_SHORT_LINKS),
                link_durability="14",
                max_custom_domains="0",
                max_onyx_subdomains="0",
                max_custom_paths="0",
                max_visits_per_shortlink="500",
                is_active=True,
                features=[{"name": "free_link", "enabled": True}],
            )
            session.add(free_tier)
            await session.flush()
            logger.info("Created default free tier")
        else:
            free_tier = existing_tier

        await session.commit()


async def assign_free_tier_to_user(session: AsyncSession, user: UserModel) -> SubscriptionModel:
    if user.current_sub_id:
        return await session.scalar(
            select(SubscriptionModel).where(SubscriptionModel.sub_id == user.current_sub_id)
        )

    tier = await session.scalar(select(TierModel).where(func.lower(TierModel.name) == "free"))
    if not tier:
        tier = TierModel(
            name="free",
            description="Default free tier",
            price=Decimal("0.00"),
            permissions=[AppPermission.FREE_LINK],
            max_short_link=str(settings.MIN_ALLOWED_SHORT_LINKS),
            link_durability="14",
            max_custom_domains="0",
            max_onyx_subdomains="0",
            max_custom_paths="0",
            max_visits_per_shortlink="500",
            is_active=True,
            features=[{"name": "free_link", "enabled": True}],
        )
        session.add(tier)
        await session.flush()

    new_subscription = SubscriptionModel(
        user_id=user.user_id,
        tier_id=tier.tier_id,
        amount=Decimal("0.00"),
        status=SUBSCRIPTION_STATUS.ACTIVE,
        idompotent_key=uuid.uuid4(),
        expired_at=datetime.now(timezone.utc) + timedelta(days=3650),
    )
    session.add(new_subscription)
    await session.flush()

    user.current_sub_id = new_subscription.sub_id
    return new_subscription
