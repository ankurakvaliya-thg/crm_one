from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_account import crud_account
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.api.deps import get_current_user, get_current_active_manager
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[AccountResponse], summary="List all organization accounts")
async def read_accounts(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    owner_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve organization accounts."""
    # Filter by user if role is SALES_REP and owner_id is requested or restricted
    if current_user.role == UserRole.SALES_REP and owner_id is None:
        owner_id = current_user.id
    accounts = await crud_account.get_multi(db, skip=skip, limit=limit, owner_id=owner_id)
    return accounts


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED, summary="Create account")
async def create_account(
    account_in: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new account/company profile."""
    if account_in.owner_id is None:
        account_in.owner_id = current_user.id
    return await crud_account.create(db, obj_in=account_in)


@router.get("/{account_id}", response_model=AccountResponse, summary="Get account by ID")
async def read_account_by_id(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get a specific account by ID."""
    account = await crud_account.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountResponse, summary="Update account details")
async def update_account(
    account_id: int,
    account_in: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update account details."""
    account = await crud_account.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return await crud_account.update(db, db_obj=account, obj_in=account_in)


@router.delete("/{account_id}", response_model=AccountResponse, summary="Delete account (Manager/Admin)")
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_manager),
) -> Any:
    """Delete an account (Manager or Admin only)."""
    account = await crud_account.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return await crud_account.delete(db, account_id=account_id)
