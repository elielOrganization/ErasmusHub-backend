from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.exemption import Exemption
from schemas.exencion_schema import ExemptionRead, ExemptionCreate

router = APIRouter(prefix="/exemptions", tags=["Exemptions"])


@router.get("/me", response_model=list[ExemptionRead])
def list_my_exemptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    items = db.exec(
        select(Exemption)
        .where(Exemption.student_id == current_user.id)
        .order_by(Exemption.created_at.desc())
    ).all()
    return [ExemptionRead.model_validate(e) for e in items]


@router.post("/", response_model=ExemptionRead)
def create_exemption(
    data: ExemptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    exemption = Exemption(
        student_id=current_user.id,
        reason=data.reason,
    )
    db.add(exemption)
    db.commit()
    db.refresh(exemption)
    return ExemptionRead.model_validate(exemption)
