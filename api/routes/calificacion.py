from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.calificacion import Calificacion
from schemas.calificacion_schema import CalificacionRead, CalificacionUpdate

router = APIRouter(prefix="/calificacion", tags=["Calificacion"])


def _require_admin(current_user: User) -> None:
    role_name = current_user.roles[0].name.lower() if current_user.roles else ""
    if "admin" not in role_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden modificar la tabla de calificación",
        )


@router.get("", response_model=CalificacionRead)
def get_calificacion(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    row = db.exec(select(Calificacion)).first()
    if not row:
        return CalificacionRead(
            id=0,
            interview=0.0,
            grade_certificate=0.0,
            motivation_letter=0.0,
            language_certificate=0.0,
            disability_certificate=0.0,
            updated_at=datetime.now(timezone.utc),
            updated_by=None,
        )
    return row


@router.put("", response_model=CalificacionRead)
def update_calificacion(
    body: CalificacionUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    row = db.exec(select(Calificacion)).first()
    if not row:
        row = Calificacion()
        db.add(row)

    row.interview = body.interview
    row.grade_certificate = body.grade_certificate
    row.motivation_letter = body.motivation_letter
    row.language_certificate = body.language_certificate
    row.disability_certificate = body.disability_certificate
    row.updated_at = datetime.now(timezone.utc)
    row.updated_by = current_user.id

    db.commit()
    db.refresh(row)
    return row
