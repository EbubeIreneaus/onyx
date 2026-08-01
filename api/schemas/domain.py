from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DomainCreate(BaseModel):
    name: str

class DomainUpdate(BaseModel):
    name: Optional[str] = None

class DomainCheckRequest(BaseModel):
    domain: str
    slug: Optional[str] = None

class DomainCheckResponse(BaseModel):
    available: bool
    txt_verified: bool
    cname_verified: bool
    message: str
    txt_verification_token: Optional[str] = None

class DomainResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    txt_verified: bool
    cname_verified: bool
    created_at: datetime
