from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime, timezone

from core.database import get_session
from core.security import get_current_user
from models.user import Usuario
from models.practica import Practicas
from models.horario_semanal import HorarioSemanal
from models.seguimiento import Seguimientos
from models.diario_practica import DiarioPractica
from models.asistencia import Asistencia
from models.comunicacion import Comunicaciones
from schemas.practica_schema import (
    PracticaList, PracticaDetail, HorarioRead,
    SeguimientoRead, SeguimientoSubmit,
    DiarioRead, DiarioCreate, DiarioUpdate,
    AsistenciaRead,
    ComunicacionRead, ComunicacionCreate,
)
from schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/practicas", tags=["Practicas"])


@router.get("/me", response_model=PaginatedResponse[PracticaList])
def list_my_practicas(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    query = select(Practicas).where(Practicas.estudiante_id == current_user.id)
    if search:
        query = query.where(Practicas.empresa_nombre.ilike(f"%{search}%"))

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(query.offset((page - 1) * page_size).limit(page_size)).all()

    return PaginatedResponse(
        items=[PracticaList.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{practica_id}", response_model=PracticaDetail)
def get_practica_detail(
    practica_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    horarios = db.exec(
        select(HorarioSemanal).where(HorarioSemanal.practica_id == practica_id)
    ).all()

    return PracticaDetail(
        id=practica.id,
        estudiante_nombre=current_user.nombre,
        estudiante_apellidos=current_user.apellidos,
        estudiante_email=current_user.email,
        empresa_nombre=practica.empresa_nombre,
        empresa_cif=practica.empresa_cif,
        empresa_direccion=practica.empresa_direccion,
        tutor_empresa_nombre=practica.tutor_empresa_nombre,
        tutor_empresa_email=practica.tutor_empresa_email,
        tutor_educativo_nombre=practica.tutor_educativo_nombre,
        fecha_inicio=practica.fecha_inicio,
        fecha_fin=practica.fecha_fin,
        horas_totales=practica.horas_totales,
        estado=practica.estado,
        horarios=[HorarioRead.model_validate(h) for h in horarios],
    )


# --- SEGUIMIENTOS ---

@router.get("/{practica_id}/seguimientos", response_model=list[SeguimientoRead])
def list_seguimientos(
    practica_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    items = db.exec(
        select(Seguimientos)
        .where(Seguimientos.practica_id == practica_id)
        .order_by(Seguimientos.fecha_programada)
    ).all()
    return [SeguimientoRead.model_validate(s) for s in items]


@router.post("/{practica_id}/seguimientos/{seg_id}/completar", response_model=SeguimientoRead)
def completar_seguimiento(
    practica_id: int,
    seg_id: int,
    data: SeguimientoSubmit,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    seg = db.get(Seguimientos, seg_id)
    if not seg or seg.practica_id != practica_id:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    seg.completado = True
    seg.fecha_completado = datetime.now(timezone.utc)
    seg.respuestas = data.respuestas
    db.add(seg)
    db.commit()
    db.refresh(seg)
    return SeguimientoRead.model_validate(seg)


# --- DIARIO ---

@router.get("/{practica_id}/diario", response_model=PaginatedResponse[DiarioRead])
def list_diario(
    practica_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    query = select(DiarioPractica).where(DiarioPractica.practica_id == practica_id)
    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(DiarioPractica.fecha.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedResponse(
        items=[DiarioRead.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{practica_id}/diario", response_model=DiarioRead)
def create_or_update_diario(
    practica_id: int,
    data: DiarioCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    # Check if entry exists for this date
    existing = db.exec(
        select(DiarioPractica)
        .where(DiarioPractica.practica_id == practica_id)
        .where(DiarioPractica.fecha == data.fecha)
    ).first()

    if existing:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        existing.estado = "completado"
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return DiarioRead.model_validate(existing)

    entry = DiarioPractica(
        practica_id=practica_id,
        estado="completado",
        **data.model_dump(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return DiarioRead.model_validate(entry)


# --- ASISTENCIA (CALENDARIO) ---

@router.get("/{practica_id}/asistencia", response_model=list[AsistenciaRead])
def list_asistencia(
    practica_id: int,
    month: Optional[str] = Query(None, description="YYYY-MM format"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    query = select(Asistencia).where(Asistencia.practica_id == practica_id)
    if month:
        # Filter by year-month
        query = query.where(
            func.to_char(Asistencia.fecha, "YYYY-MM") == month
        )
    items = db.exec(query.order_by(Asistencia.fecha)).all()
    return [AsistenciaRead.model_validate(a) for a in items]


# --- COMUNICACIONES ---

@router.get("/{practica_id}/comunicaciones", response_model=list[ComunicacionRead])
def list_comunicaciones(
    practica_id: int,
    destinatario_tipo: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    query = select(Comunicaciones).where(Comunicaciones.practica_id == practica_id)
    if destinatario_tipo:
        query = query.where(Comunicaciones.destinatario_tipo == destinatario_tipo)
    items = db.exec(query.order_by(Comunicaciones.created_at.desc())).all()
    return [ComunicacionRead.model_validate(c) for c in items]


@router.post("/{practica_id}/comunicaciones", response_model=ComunicacionRead)
def create_comunicacion(
    practica_id: int,
    data: ComunicacionCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    practica = db.get(Practicas, practica_id)
    if not practica or practica.estudiante_id != current_user.id:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")

    com = Comunicaciones(
        practica_id=practica_id,
        emisor_id=current_user.id,
        **data.model_dump(),
    )
    db.add(com)
    db.commit()
    db.refresh(com)
    return ComunicacionRead.model_validate(com)
