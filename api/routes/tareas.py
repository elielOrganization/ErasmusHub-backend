from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional

from core.database import get_session
from core.security import get_current_user
from models.user import Usuario
from models.task import Tareas
from schemas.task_schema import TaskRead
from schemas.pagination import PaginatedResponse


router = APIRouter(prefix="/tareas", tags=["Tareas"])


@router.get("/me", response_model=PaginatedResponse[TaskRead])
def list_my_tareas(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    query = select(Tareas).where(Tareas.user_id == current_user.id)
    if search:
        query = query.where(Tareas.titulo.ilike(f"%{search}%"))

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(Tareas.due_date)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedResponse(
        items=[TaskRead.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{tarea_id}/completar", response_model=TaskRead)
def completar_tarea(
    tarea_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    tarea = db.get(Tareas, tarea_id)
    if not tarea or tarea.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    tarea.completed = True
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return TaskRead.model_validate(tarea)
