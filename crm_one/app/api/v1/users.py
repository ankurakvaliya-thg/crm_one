from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_user import crud_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.api.deps import get_current_user, get_current_active_manager, check_roles
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[UserResponse], summary="List all users")
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_manager),
) -> Any:
    """Retrieve users (Manager/Admin permission required)."""
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user (Admin only)")
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_roles([UserRole.ADMIN])),
) -> Any:
    """Create new user (Admin permission required)."""
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    return await crud_user.create(db, obj_in=user_in)


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get a specific user by ID."""
    user = await crud_user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.role == UserRole.SALES_REP and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="Update user details")
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update user profile (Self or Admin required)."""
    user = await crud_user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Non-admins cannot elevate roles or deactivate accounts
    if current_user.role != UserRole.ADMIN:
        user_in.role = None
        user_in.is_active = None

    return await crud_user.update(db, db_obj=user, obj_in=user_in)
