from typing import TYPE_CHECKING
from schemas.user import SUBSCRIPTION_STATUS
from schemas.user import USER_STATUS
from email.policy import default
from datetime import datetime
from sqlalchemy import Numeric
from decimal import Decimal
from enum import unique
import uuid
from typing import List
from typing import Optional
from .db import Base
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, func, Enum, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import EmailStr
from schemas.user import SUBSCRIPTION_TIER


if TYPE_CHECKING:
    from .redirect import Redirect, Domain
    from .admin import Tier

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, index=True, unique=True)
    fullname: Mapped[str] = mapped_column(String(50))
    email: Mapped[EmailStr] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(100))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[USER_STATUS] = mapped_column(Enum(USER_STATUS), default=USER_STATUS.ACTIVE)
    current_sub_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("subscriptions.sub_id"), nullable=True)
    current_subscription: Mapped[Optional['Subscription']] = relationship(foreign_keys=[current_sub_id])
    subscriptions: Mapped[List['Subscription']] = relationship(back_populates="user", foreign_keys="[Subscription.user_id]", cascade="all, delete-orphan")
    redirects: Mapped[List['Redirect']] = relationship(back_populates="user", cascade="all, delete-orphan")
    domains: Mapped[List['Domain']] = relationship(back_populates="user", cascade="all, delete-orphan")    
    sessions: Mapped[List['Session']] = relationship(back_populates="user", cascade="all, delete-orphan")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sub_id: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.user_id"), index=True)
    user: Mapped['User'] = relationship(back_populates="subscriptions", foreign_keys=[user_id])
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[SUBSCRIPTION_STATUS] = mapped_column(Enum(SUBSCRIPTION_STATUS), default=SUBSCRIPTION_STATUS.UNPAID)
    idompotent_key: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, index=True)
    tier_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("tiers.tier_id"), index=True)
    tier: Mapped['Tier'] = relationship()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.user_id"), index=True)
    user: Mapped['User'] = relationship(back_populates="sessions")
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    
 
    