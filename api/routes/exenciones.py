from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_current_user
from models.user import Usuario
from models.exencion import Exenciones
from schemas.exencion_schema import ExencionRead, ExencionCreate

router = APIRouter(prefix="/exenciones", tags=["Exenciones"])


@router.get("/me", response_model=list[ExencionRead])
def list_my_exenciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    items = db.exec(
        select(Exenciones)
        .where(Exenciones.estudiante_id == current_user.id)
        .order_by(Exenciones.created_at.desc())
    ).all()
    return [ExencionRead.model_validate(e) for e in items]


@router.post("/", response_model=ExencionRead)
def create_exencion(
    data: ExencionCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    exencion = Exenciones(
        estudiante_id=current_user.id,
        motivo=data.motivo,
    )
    db.add(exencion)
    db.commit()
    db.refresh(exencion)
    return ExencionRead.model_validate(exencion)
