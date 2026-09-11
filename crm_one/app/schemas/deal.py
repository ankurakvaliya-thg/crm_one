from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.deal import DealStage


class DealBase(BaseModel):
    title: str
    amount: float = 0.0
    stage: DealStage = DealStage.QUALIFICATION
    probability: int = 10
    expected_close_date: Optional[datetime] = None
    account_id: Optional[int] = None
    contact_id: Optional[int] = None
    owner_id: Optional[int] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    stage: Optional[DealStage] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    account_id: Optional[int] = None
    contact_id: Optional[int] = None
    owner_id: Optional[int] = None


class DealResponse(DealBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
