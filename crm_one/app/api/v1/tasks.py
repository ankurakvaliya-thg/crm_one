from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_task import crud_task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.models.task import TaskStatus, TaskPriority
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[TaskResponse], summary="List all tasks and activities")
async def read_tasks(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve tasks and activity items."""
    if current_user.role == UserRole.SALES_REP and assigned_to_id is None:
        assigned_to_id = current_user.id
    return await crud_task.get_multi(
        db, skip=skip, limit=limit, status=status, priority=priority, assigned_to_id=assigned_to_id
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create a task or activity")
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new task, call reminder, or meeting item."""
    if task_in.assigned_to_id is None:
        task_in.assigned_to_id = current_user.id
    return await crud_task.create(db, obj_in=task_in)


@router.get("/{task_id}", response_model=TaskResponse, summary="Get task by ID")
async def read_task_by_id(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get task details by ID."""
    task = await crud_task.get(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse, summary="Update task status or details")
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update task details, mark as completed, or reassign."""
    task = await crud_task.get(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await crud_task.update(db, db_obj=task, obj_in=task_in)


@router.delete("/{task_id}", response_model=TaskResponse, summary="Delete task")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Delete a task."""
    task = await crud_task.get(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await crud_task.delete(db, task_id=task_id)
