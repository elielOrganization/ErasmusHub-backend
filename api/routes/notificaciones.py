from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional
from pydantic import BaseModel

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.notification import Notification
from schemas.notification_schema import NotificationRead
from schemas.pagination import PaginatedResponse


class UnreadCount(BaseModel):
    count: int


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=PaginatedResponse[NotificationRead])
def list_my_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if search:
        query = query.where(Notification.title.ilike(f"%{search}%"))

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedResponse(
        items=[NotificationRead.model_validate(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/me/unread-count", response_model=UnreadCount)
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    count = db.exec(
        select(func.count())
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)
    ).one()
    return UnreadCount(count=count)


@router.patch("/{notif_id}/read", response_model=NotificationRead)
def mark_as_read(
    notif_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    notif = db.get(Notification, notif_id)
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return NotificationRead.model_validate(notif)
