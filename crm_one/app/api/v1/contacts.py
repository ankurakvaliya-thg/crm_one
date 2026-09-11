from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_contact import crud_contact
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[ContactResponse], summary="List all contacts")
async def read_contacts(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    account_id: Optional[int] = Query(None),
    owner_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve contacts."""
    if current_user.role == UserRole.SALES_REP and owner_id is None:
        owner_id = current_user.id
    return await crud_contact.get_multi(db, skip=skip, limit=limit, account_id=account_id, owner_id=owner_id)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, summary="Create contact")
async def create_contact(
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new contact."""
    if contact_in.owner_id is None:
        contact_in.owner_id = current_user.id
    return await crud_contact.create(db, obj_in=contact_in)


@router.get("/{contact_id}", response_model=ContactResponse, summary="Get contact by ID")
async def read_contact_by_id(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get a specific contact by ID."""
    contact = await crud_contact.get(db, contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, summary="Update contact details")
async def update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update contact details."""
    contact = await crud_contact.get(db, contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return await crud_contact.update(db, db_obj=contact, obj_in=contact_in)


@router.delete("/{contact_id}", response_model=ContactResponse, summary="Delete contact")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Delete a contact."""
    contact = await crud_contact.get(db, contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return await crud_contact.delete(db, contact_id=contact_id)
