from permission import AdminPermission
from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from typing import Optional, List
from datetime import datetime
import uuid
from decimal import Decimal
from permission import AppPermission

class SUBSCRIPTION_TIER(str, Enum):
    FREE = "free"
    TRIAL = "trial"
    PREMIUM = "premium"
    PRO = "pro"

class SUBSCRIPTION_STATUS(str, Enum):
    ACTIVE = "active"
    UNPAID = "unpaid"
    TRAILING = "trailing"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"

class USER_STATUS(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    DELETED = "deleted"

class BaseUser(BaseModel):
    fullname: str
    email: EmailStr

class UserCreate(BaseUser):
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ChangePassIn(BaseModel):
    current: str
    new_password: str

class ResetLinkIn(BaseModel):
    email: EmailStr

class ResetPassIn(BaseModel):
    token: str
    new_password: str

class TierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tier_id: uuid.UUID
    name: str
    price: Decimal
    permissions: List[AppPermission]
    max_short_link: str
    link_durability: Optional[str] = "14"
    max_custom_domains: Optional[str] = "0"
    max_onyx_subdomains: Optional[str] = "0"
    max_custom_paths: Optional[str] = "0"
    max_visits_per_shortlink: Optional[str] = "500"
    is_active: bool

class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sub_id: uuid.UUID
    amount: Decimal
    status: SUBSCRIPTION_STATUS
    tier_id: uuid.UUID
    tier: Optional[TierOut] = None
    created_at: datetime
    expired_at: datetime

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: uuid.UUID
    fullname: str
    email: EmailStr
    status: USER_STATUS
    email_verified: bool
    created_at: datetime
    current_subscription: Optional[SubscriptionOut] = None

class UserManage(UserOut):
    model_config = ConfigDict(from_attributes=True)
    is_admin: bool
    admin_priviledges: Optional[List[AdminPermission]] = None

class SessionUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: uuid.UUID
    user_id: uuid.UUID
    user: UserManage
    expires_at: datetime