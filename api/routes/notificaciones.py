from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional

from core.database import get_session
from core.security import get_current_user
from models.user import Usuario
from models.notifications import Notificaciones
from schemas.pagination import PaginatedResponse
from pydantic import BaseModel
from datetime import datetime


class NotificacionRead(BaseModel):
    id: int
    titulo: str
    body: str
    tipo: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UnreadCount(BaseModel):
    count: int


router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("/me", response_model=PaginatedResponse[NotificacionRead])
def list_my_notificaciones(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    query = select(Notificaciones).where(Notificaciones.user_id == current_user.id)
    if search:
        query = query.where(Notificaciones.titulo.ilike(f"%{search}%"))

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(Notificaciones.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedResponse(
        items=[NotificacionRead.model_validate(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/me/unread-count", response_model=UnreadCount)
def unread_count(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    count = db.exec(
        select(func.count())
        .where(Notificaciones.user_id == current_user.id)
        .where(Notificaciones.is_read == False)
    ).one()
    return UnreadCount(count=count)


@router.patch("/{notif_id}/read", response_model=NotificacionRead)
def mark_as_read(
    notif_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    notif = db.get(Notificaciones, notif_id)
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    notif.is_read = True
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return NotificacionRead.model_validate(notif)
