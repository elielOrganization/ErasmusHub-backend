from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.application import Application
from models.opportunity import Opportunity
from models.document import Document
from models.application_document import ApplicationDocument
from schemas.application_schema import ApplicationCreate, ApplicationList, ApplicationDetail, ApplicationWithStudent, ReassignRequest
from schemas.document_schema import DocumentRead

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


@router.get("/all", response_model=list[ApplicationWithStudent])
def list_all_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    rows = db.exec(
        select(Application, User, Opportunity)
        .join(User, Application.user_id == User.id)
        .join(Opportunity, Application.opportunity_id == Opportunity.id)
    ).all()
    return [
        ApplicationWithStudent(
            application_id=app.id,
            opportunity_id=opp.id,
            opportunity_name=opp.name,
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            status=app.status,
        )
        for app, user, opp in rows
    ]


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
    opportunity = db.get(Opportunity, data.opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    if opportunity.status != "open":
        raise HTTPException(status_code=400, detail="This opportunity is not open for applications")

    if opportunity.filled_slots >= opportunity.max_slots:
        raise HTTPException(status_code=400, detail="No available slots for this opportunity")

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
    opportunity.filled_slots += 1
    db.add(opportunity)
    db.commit()
    db.refresh(application)
    return ApplicationDetail.model_validate(application)

@router.patch("/reassign", response_model=ApplicationDetail)
def reassign_application(
    data: ReassignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    existing = db.exec(
        select(Application).where(Application.user_id == data.user_id)
    ).first()
    if existing:
        old_opp = db.get(Opportunity, existing.opportunity_id)
        if old_opp and old_opp.filled_slots > 0:
            old_opp.filled_slots -= 1
            db.add(old_opp)
        db.delete(existing)

    new_opp = db.get(Opportunity, data.new_opportunity_id)
    if not new_opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    application = Application(
        user_id=data.user_id,
        opportunity_id=data.new_opportunity_id,
        status="pending",
    )
    db.add(application)
    new_opp.filled_slots += 1
    db.add(new_opp)
    db.commit()
    db.refresh(application)
    return ApplicationDetail.model_validate(application)


# ── Document Library endpoints ─────────────────────────────────────────────────

@router.get("/{app_id}/documents", response_model=list[DocumentRead])
def list_application_documents(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    app = db.get(Application, app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    links = db.exec(
        select(ApplicationDocument).where(ApplicationDocument.application_id == app_id)
    ).all()

    docs = []
    for link in links:
        doc = db.get(Document, link.document_id)
        if doc:
            docs.append(DocumentRead.model_validate(doc))
    return docs


@router.post("/{app_id}/documents/{doc_id}", status_code=status.HTTP_201_CREATED)
def attach_document(
    app_id: int,
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    app = db.get(Application, app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    doc = db.get(Document, doc_id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found in your library")

    existing = db.get(ApplicationDocument, (app_id, doc_id))
    if existing:
        raise HTTPException(status_code=400, detail="Document already attached to this application")

    link = ApplicationDocument(application_id=app_id, document_id=doc_id)
    db.add(link)
    db.commit()
    return {"ok": True}


@router.delete("/{app_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_document(
    app_id: int,
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    app = db.get(Application, app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    link = db.get(ApplicationDocument, (app_id, doc_id))
    if not link:
        raise HTTPException(status_code=404, detail="Document not attached to this application")

    db.delete(link)
    db.commit()
