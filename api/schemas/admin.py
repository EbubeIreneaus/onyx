from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal
from permission import AppPermission
from datetime import datetime
import uuid
from setting import settings

class TierCreate(BaseModel):
    name: str
    price: float
    permissions: List[AppPermission]
    max_short_link: str = "100"
    link_durability: str = "14"
    max_custom_domains: str = "0"
    max_onyx_subdomains: str = "0"
    max_custom_paths: str = "0"
    max_visits_per_shortlink: str = "500"
    description: Optional[str] = None
    is_active: bool = True

class TierUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    permissions: Optional[List[AppPermission]] = None
    max_short_link: Optional[str] = None
    link_durability: Optional[str] = None
    max_custom_domains: Optional[str] = None
    max_onyx_subdomains: Optional[str] = None
    max_custom_paths: Optional[str] = None
    max_visits_per_shortlink: Optional[str] = None
    is_active: Optional[bool] = None

class TierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tier_id: uuid.UUID
    name: str
    price: Decimal
    permissions: List[AppPermission]
    max_short_link: str
    link_durability: str
    max_custom_domains: str
    max_onyx_subdomains: str
    max_custom_paths: str
    max_visits_per_shortlink: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class SubscribeIn(BaseModel):
    tier_id: uuid.UUID
    callback_url: Optional[str] = None

class AdminAnalyticsResponse(BaseModel):
    total_users: int
    active_users: int
    suspended_users: int
    total_redirects: int
    total_visits: int
    total_domains: int
    verified_domains: int
    active_tiers_count: int

class UserStatusUpdate(BaseModel):
    status: str # "ACTIVE" or "SUSPENDED"

class UserRoleUpdate(BaseModel):
    is_admin: bool
    admin_privileges: Optional[List[str]] = None

class UserTierUpdate(BaseModel):
    tier_id: uuid.UUID

class AdminUserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: uuid.UUID
    fullname: str
    email: str
    is_admin: Optional[bool] = False
    status: str
    tier_name: Optional[str] = None
    created_at: datetime
    redirects_count: int = 0
    domains_count: int = 0

class AdminDomainListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    user_email: str
    txt_verified: bool
    cname_verified: bool
    is_root_domain: bool
    created_at: datetime

class AdminRedirectListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    domain: str
    slug: str
    destination: str
    visits: int
    expired: bool
    user_email: str
    created_at: datetime
