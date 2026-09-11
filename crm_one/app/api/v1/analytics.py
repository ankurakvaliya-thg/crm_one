from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analytics import DashboardMetrics, StageSummary
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStage
from app.models.account import Account
from app.models.contact import Contact
from app.models.task import Task, TaskStatus
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics, summary="Get CRM analytics dashboard metrics")
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve comprehensive CRM dashboard analytics and sales pipeline metrics."""
    
    # 1. Lead counts
    total_leads_res = await db.execute(select(func.count(Lead.id)))
    total_leads = total_leads_res.scalar_one() or 0

    new_leads_res = await db.execute(select(func.count(Lead.id)).where(Lead.status == LeadStatus.NEW))
    new_leads = new_leads_res.scalar_one() or 0

    converted_leads_res = await db.execute(select(func.count(Lead.id)).where(Lead.status == LeadStatus.CONVERTED))
    converted_leads = converted_leads_res.scalar_one() or 0

    lead_conversion_rate = round((converted_leads / total_leads * 100), 2) if total_leads > 0 else 0.0

    # 2. Deal counts & revenue
    total_deals_res = await db.execute(select(func.count(Deal.id)))
    total_deals = total_deals_res.scalar_one() or 0

    open_deals_res = await db.execute(
        select(func.sum(Deal.amount)).where(
            Deal.stage.notin_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST])
        )
    )
    open_deals_amount = open_deals_res.scalar_one() or 0.0

    closed_won_res = await db.execute(
        select(func.sum(Deal.amount)).where(Deal.stage == DealStage.CLOSED_WON)
    )
    closed_won_amount = closed_won_res.scalar_one() or 0.0

    # 3. Pipeline distribution by stage
    pipeline_res = await db.execute(
        select(Deal.stage, func.count(Deal.id), func.sum(Deal.amount)).group_by(Deal.stage)
    )
    pipeline_by_stage = [
        StageSummary(
            stage=stage.value if hasattr(stage, "value") else str(stage),
            count=count,
            total_amount=amount or 0.0
        )
        for stage, count, amount in pipeline_res.all()
    ]

    # 4. Account, Contact, and Task totals
    total_accounts_res = await db.execute(select(func.count(Account.id)))
    total_accounts = total_accounts_res.scalar_one() or 0

    total_contacts_res = await db.execute(select(func.count(Contact.id)))
    total_contacts = total_contacts_res.scalar_one() or 0

    pending_tasks_res = await db.execute(
        select(func.count(Task.id)).where(Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]))
    )
    pending_tasks = pending_tasks_res.scalar_one() or 0

    return DashboardMetrics(
        total_leads=total_leads,
        new_leads=new_leads,
        converted_leads=converted_leads,
        lead_conversion_rate=lead_conversion_rate,
        total_deals=total_deals,
        open_deals_amount=open_deals_amount,
        closed_won_amount=closed_won_amount,
        pipeline_by_stage=pipeline_by_stage,
        total_accounts=total_accounts,
        total_contacts=total_contacts,
        pending_tasks=pending_tasks,
    )
