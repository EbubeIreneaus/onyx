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
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    permissions: Mapped[List[AppPermission]] = mapped_column(JSON)
    max_short_link: Mapped[int] = mapped_column(Integer, default=settings.MIN_ALLOWED_SHORT_LINKS)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    