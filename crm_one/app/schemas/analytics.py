from typing import Dict, List, Any
from pydantic import BaseModel


class StageSummary(BaseModel):
    stage: str
    count: int
    total_amount: float


class DashboardMetrics(BaseModel):
    total_leads: int
    new_leads: int
    converted_leads: int
    lead_conversion_rate: float
    total_deals: int
    open_deals_amount: float
    closed_won_amount: float
    pipeline_by_stage: List[StageSummary]
    total_accounts: int
    total_contacts: int
    pending_tasks: int
