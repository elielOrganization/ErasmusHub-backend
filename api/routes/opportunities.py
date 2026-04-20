from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional

from core.database import get_session
from core.security import get_current_user, get_optional_current_user
from models.user import User
from models.opportunity import Opportunity
from models.application import Application
from schemas.opportunity_schema import OpportunityCreate, OpportunityList, OpportunityDetail, OpportunityUpdate, OpportunityDelete
from schemas.application_schema import ApplicationWithStudent
from schemas.pagination import PaginatedResponse
from models.user_role import UserRole

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("/", response_model=PaginatedResponse[OpportunityList])
def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    country: Optional[str] = None,
    all: bool = Query(False, description="Return all statuses (requires auth)"),
    db: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    query = select(Opportunity)

    # Authenticated users with all=true see every status.
    # Everyone else sees only open opportunities.
    if not (all and current_user):
        query = query.where(Opportunity.status == "open")

    if search:
        query = query.where(Opportunity.name.ilike(f"%{search}%"))
    if country:
        query = query.where(Opportunity.country == country)

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(Opportunity.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedResponse(
        items=[OpportunityList.model_validate(o) for o in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{opp_id}", response_model=OpportunityDetail)
def get_opportunity(opp_id: int, db: Session = Depends(get_session)):
    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return OpportunityDetail.model_validate(opp)


@router.post("/", response_model=OpportunityDetail)
def create_opportunity(
    data: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    opp = Opportunity(
        **data.model_dump(),
        creator_id=current_user.id,
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return OpportunityDetail.model_validate(opp)


@router.get("/{opp_id}/applications", response_model=list[ApplicationWithStudent])
def list_opportunity_applications(
    opp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    rows = db.exec(
        select(Application, User)
        .join(User, Application.user_id == User.id)
        .where(Application.opportunity_id == opp_id)
    ).all()

    return [
        ApplicationWithStudent(
            application_id=app.id,
            opportunity_id=opp_id,
            opportunity_name=opp.name,
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            status=app.status,
        )
        for app, user in rows
    ]


@router.patch("/{opp_id}", response_model=OpportunityDetail)
def update_opportunity(
    opp_id: int,
    data: OpportunityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if opp.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this opportunity")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(opp, key, value)

    db.add(opp)
    db.commit()
    db.refresh(opp)
    return OpportunityDetail.model_validate(opp)

@router.delete("/{opp_id}", response_model=OpportunityDelete)
def delete_opportunity(
    opp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    opp = db.get(Opportunity, opp_id)

    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    role = db.exec(select(UserRole).where(UserRole.user_id == current_user.id)).first()

    if role.role_id != 1:
        raise HTTPException(status_code=403, detail="You have no rights to delete an opportunity")
    
    response_data = OpportunityDelete.model_validate(opp)

    db.delete(opp)
    db.commit()
    return response_data
    