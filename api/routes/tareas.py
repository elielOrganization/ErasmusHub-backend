from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.task import Task
from schemas.task_schema import TaskRead
from schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/me", response_model=PaginatedResponse[TaskRead])
def list_my_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    query = select(Task).where(Task.user_id == current_user.id)
    if search:
        query = query.where(Task.title.ilike(f"%{search}%"))

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(Task.due_date)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedResponse(
        items=[TaskRead.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    task = db.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskRead.model_validate(task)
