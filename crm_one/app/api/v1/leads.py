from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_lead import crud_lead
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadConvertResponse
from app.models.lead import LeadStatus
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[LeadResponse], summary="List all leads")
async def read_leads(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[LeadStatus] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve sales leads."""
    if current_user.role == UserRole.SALES_REP and assigned_to_id is None:
        assigned_to_id = current_user.id
    return await crud_lead.get_multi(db, skip=skip, limit=limit, status=status, assigned_to_id=assigned_to_id)


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED, summary="Create a lead")
async def create_lead(
    lead_in: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new sales lead."""
    if lead_in.assigned_to_id is None:
        lead_in.assigned_to_id = current_user.id
    return await crud_lead.create(db, obj_in=lead_in)


@router.get("/{lead_id}", response_model=LeadResponse, summary="Get lead by ID")
async def read_lead_by_id(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get lead by ID."""
    lead = await crud_lead.get(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse, summary="Update lead details")
async def update_lead(
    lead_id: int,
    lead_in: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update lead information or stage status."""
    lead = await crud_lead.get(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return await crud_lead.update(db, db_obj=lead, obj_in=lead_in)


@router.delete("/{lead_id}", response_model=LeadResponse, summary="Delete lead")
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Delete a lead."""
    lead = await crud_lead.get(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return await crud_lead.delete(db, lead_id=lead_id)


@router.post("/{lead_id}/convert", response_model=LeadConvertResponse, summary="Convert Lead into Account, Contact, and Deal")
async def convert_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Convert a qualified lead automatically into an Account, Contact, and Deal."""
    lead = await crud_lead.get(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    if lead.status == LeadStatus.CONVERTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lead has already been converted")
    
    lead, account, contact, deal = await crud_lead.convert(db, lead=lead)
    
    return {
        "message": "Lead successfully converted to Account, Contact, and Deal",
        "lead_id": lead.id,
        "account_id": account.id,
        "contact_id": contact.id,
        "deal_id": deal.id,
    }
