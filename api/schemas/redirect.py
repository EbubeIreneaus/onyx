from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class RedirectCreate(BaseModel):
    destination: str
    domain: Optional[str] = None
    slug: Optional[str] = None
    type: Optional[str] = None
    expired_on: Optional[datetime] = None

class RedirectUpdate(BaseModel):
    destination: Optional[str] = None
    slug: Optional[str] = None
    expired: Optional[bool] = None
    expired_on: Optional[datetime] = None

class RedirectVisitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ip: str
    location: Optional[str] = None
    device: Optional[str] = None
    created_at: datetime

class RedirectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    redirect_id: uuid.UUID
    domain: str
    slug: Optional[str] = None
    destination: str
    expired: bool
    expired_on: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    visitor_count: Optional[int] = 0

class RedirectResolveRequest(BaseModel):
    domain: str
    slug: Optional[str] = None
    full_url: Optional[str] = None

class RedirectResolveResponse(BaseModel):
    found: bool
    destination: Optional[str] = None
    expired: bool = False
    message: Optional[str] = None

class TimeSeriesPoint(BaseModel):
    date: str
    visits: int

class CountryAnalytics(BaseModel):
    country: str
    visits: int
    percentage: float

class DeviceAnalytics(BaseModel):
    device: str
    visits: int

class RedirectAnalyticsResponse(BaseModel):
    redirect_id: str
    domain: str
    slug: Optional[str] = None
    destination: str
    expired: bool
    expired_on: Optional[datetime] = None
    created_at: datetime
    total_clicks: int
    unique_visitors: int
    top_country: Optional[str] = None
    top_device: Optional[str] = None
    chart_data: List[TimeSeriesPoint]
    country_data: List[CountryAnalytics]
    device_data: List[DeviceAnalytics]
    recent_visitors: List[RedirectVisitorResponse]
