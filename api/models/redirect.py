from email.policy import default
from sqlalchemy.orm import Relationship
from typing import Optional
from datetime import datetime
from pydantic import HttpUrl
from enum import unique
from typing import TYPE_CHECKING
from setting import settings
from enum import Enum
from typing import List
import uuid
from sqlalchemy import Integer, String, Numeric, Boolean, DateTime, func, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.db import Base

if TYPE_CHECKING:
    from .user import User

class Domain(Base):
    __tablename__="domains"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.user_id"), index=True)
    user: Mapped['User'] = relationship(back_populates="domains")
    txt_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    cname_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Redirect(Base):
    __tablename__ = "redirects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    redirect_id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('users.user_id'), index=True)
    user: Mapped['User'] = relationship(back_populates="redirects")
    domain: Mapped[str] = mapped_column(String(60), default=settings.DOMAIN_NAME)
    slug: Mapped[str] = mapped_column(String(50), index=True, unique=False, nullable=True)
    destination: Mapped[str] = mapped_column(String)
    qr_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expired: Mapped[bool] = mapped_column(Boolean, default=False)
    expired_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    visitors: Mapped[List['RedirectVisitors']] = relationship(back_populates="redirect", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("domain", "slug", name="idx_domain_slug"),
    )

class RedirectVisitors(Base):
    __tablename__="redirect_visitors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    redirect_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('redirects.redirect_id'))
    redirect: Mapped["Redirect"] = relationship(back_populates="visitors")
    ip: Mapped[str] = mapped_column(String)
    location: Mapped[Optional[str]] =  mapped_column(String, nullable=True)
    device: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
