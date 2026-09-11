from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AccountBase(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    annual_revenue: Optional[float] = None
    employees_count: Optional[int] = None
    owner_id: Optional[int] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    annual_revenue: Optional[float] = None
    employees_count: Optional[int] = None
    owner_id: Optional[int] = None


class AccountResponse(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
