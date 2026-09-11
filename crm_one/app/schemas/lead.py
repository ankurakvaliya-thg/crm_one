from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.lead import LeadStatus


class LeadBase(BaseModel):
    title: str
    company_name: Optional[str] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    estimated_value: Optional[float] = 0.0
    assigned_to_id: Optional[int] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[LeadStatus] = None
    estimated_value: Optional[float] = None
    assigned_to_id: Optional[int] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadConvertResponse(BaseModel):
    message: str
    lead_id: int
    account_id: int
    contact_id: int
    deal_id: Optional[int] = None
