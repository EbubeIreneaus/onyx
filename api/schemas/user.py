from pydantic import BaseModel, EmailStr
from enum import Enum

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