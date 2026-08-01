from typing import Optional
from setting import settings
from enum import Enum
from typing import List
import uuid
from sqlalchemy import Integer, String, Numeric, Boolean, DateTime, func, UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column
from models.db import Base
from decimal import Decimal
from permission import AppPermission

class Tier(Base):
    __tablename__ = "tiers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tier_id: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    permissions: Mapped[List[AppPermission]] = mapped_column(JSON)
    paystack_plan_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    max_short_link: Mapped[str] = mapped_column(String(50))
    link_durability: Mapped[Optional[str]] = mapped_column(String(50), default="14") #in days
    max_custom_domains: Mapped[str] = mapped_column(String(50), default="0")
    max_onyx_subdomains: Mapped[str] = mapped_column(String(50), default="0")
    max_custom_paths: Mapped[str] = mapped_column(String(50), default="0")
    max_visits_per_shortlink: Mapped[str] = mapped_column(String(50), default="500") #per day
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    features: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)

    deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    