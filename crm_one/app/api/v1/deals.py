from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_deal import crud_deal
from app.schemas.deal import DealCreate, DealUpdate, DealResponse
from app.models.deal import DealStage
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[DealResponse], summary="List all sales deals")
async def read_deals(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    stage: Optional[DealStage] = Query(None),
    owner_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve sales pipeline deals."""
    if current_user.role == UserRole.SALES_REP and owner_id is None:
        owner_id = current_user.id
    return await crud_deal.get_multi(db, skip=skip, limit=limit, stage=stage, owner_id=owner_id)


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED, summary="Create a new deal")
async def create_deal(
    deal_in: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new opportunity/deal."""
    if deal_in.owner_id is None:
        deal_in.owner_id = current_user.id
    return await crud_deal.create(db, obj_in=deal_in)


@router.get("/{deal_id}", response_model=DealResponse, summary="Get deal by ID")
async def read_deal_by_id(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get a specific deal by ID."""
    deal = await crud_deal.get(db, deal_id=deal_id)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal


@router.put("/{deal_id}", response_model=DealResponse, summary="Update deal details or stage")
async def update_deal(
    deal_id: int,
    deal_in: DealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update deal amount, probability, or pipeline stage."""
    deal = await crud_deal.get(db, deal_id=deal_id)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return await crud_deal.update(db, db_obj=deal, obj_in=deal_in)


@router.delete("/{deal_id}", response_model=DealResponse, summary="Delete deal")
async def delete_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Delete a deal."""
    deal = await crud_deal.get(db, deal_id=deal_id)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return await crud_deal.delete(db, deal_id=deal_id)
