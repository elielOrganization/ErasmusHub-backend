from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_current_user
from models.user import Usuario
from models.request import Solicitudes
from schemas.application_schema import ApplicationCreate, ApplicationList, ApplicationDetail

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/me", response_model=list[ApplicationList])
def list_my_applications(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    items = db.exec(
        select(Solicitudes)
        .where(Solicitudes.estudiante_id == current_user.id)
        .order_by(Solicitudes.submitted_at.desc())
    ).all()
    return [ApplicationList.model_validate(a) for a in items]


@router.get("/{app_id}", response_model=ApplicationDetail)
def get_application(
    app_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    app = db.get(Solicitudes, app_id)
    if not app or app.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return ApplicationDetail.model_validate(app)


@router.post("/", response_model=ApplicationDetail, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    existing = db.exec(
        select(Solicitudes)
        .where(Solicitudes.estudiante_id == current_user.id)
        .where(Solicitudes.oportunidades_id == data.oportunidades_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud para esta oportunidad")

    solicitud = Solicitudes(
        estudiante_id=current_user.id,
        oportunidades_id=data.oportunidades_id,
        status="pending",
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return ApplicationDetail.model_validate(solicitud)
