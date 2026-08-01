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
