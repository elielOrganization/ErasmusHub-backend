from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional

from core.database import get_session
from core.security import get_current_user
from models.user import Usuario
from models.opportunity import Oportunidades
from schemas.opportunity_schema import OpportunityCreate, OpportunityList, OpportunityDetail, OpportunityUpdate
from schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("/", response_model=PaginatedResponse[OpportunityList])
def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    pais: Optional[str] = None,
    db: Session = Depends(get_session),
):
    query = select(Oportunidades).where(Oportunidades.estado == "open")
    if search:
        query = query.where(Oportunidades.titulo.ilike(f"%{search}%"))
    if pais:
        query = query.where(Oportunidades.pais == pais)

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(Oportunidades.created_at.desc())
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
def get_opportunity(
    opp_id: int,
    db: Session = Depends(get_session),
):
    opp = db.get(Oportunidades, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    return OpportunityDetail.model_validate(opp)


@router.post("/", response_model=OpportunityDetail)
def create_opportunity(
    data: OpportunityCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    opp = Oportunidades(
        **data.model_dump(),
        created_by=current_user.id,
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return OpportunityDetail.model_validate(opp)


@router.patch("/{opp_id}", response_model=OpportunityDetail)
def update_opportunity(
    opp_id: int,
    data: OpportunityUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    opp = db.get(Oportunidades, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    if opp.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Sin permisos para editar esta oportunidad")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(opp, key, value)

    db.add(opp)
    db.commit()
    db.refresh(opp)
    return OpportunityDetail.model_validate(opp)
