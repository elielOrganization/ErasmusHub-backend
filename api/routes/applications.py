from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.application import Application
from schemas.application_schema import ApplicationCreate, ApplicationList, ApplicationDetail

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/me", response_model=list[ApplicationList])
def list_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    items = db.exec(
        select(Application)
        .where(Application.user_id == current_user.id)
        .order_by(Application.applied_at.desc())
    ).all()
    return [ApplicationList.model_validate(a) for a in items]


@router.get("/{app_id}", response_model=ApplicationDetail)
def get_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    app = db.get(Application, app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    return ApplicationDetail.model_validate(app)


@router.post("/", response_model=ApplicationDetail, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_session),
):
    existing = db.exec(
        select(Application)
        .where(Application.user_id == data.user_id)
        .where(Application.opportunity_id == data.opportunity_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have an application for this opportunity")

    application = Application(
        user_id=data.user_id,
        opportunity_id=data.opportunity_id,
        status="pending",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return ApplicationDetail.model_validate(application)
