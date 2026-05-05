from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select, delete
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.selection_process import SelectionProcess

from models.calificacion import Calificacion
from models.document import Document
from models.final_list import FinalList
from models.interview import Interview

router = APIRouter(prefix="/selection-process", tags=["Selection Process"])


class SelectionProcessStatus(BaseModel):
    active: bool
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    is_scheduled: bool = False


class ScheduleRequest(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


def _get_or_create_process(db: Session) -> SelectionProcess:
    process = db.exec(select(SelectionProcess).order_by(SelectionProcess.id.desc())).first()
    if not process:
        process = SelectionProcess(active=False)
        db.add(process)
        db.commit()
        db.refresh(process)
    return process


def _require_admin(current_user: User):
    if not any(role.name.lower() in ['admin', 'administrator'] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar el proceso")


def _check_and_apply_schedule(process: SelectionProcess, db: Session) -> bool:
    """Auto-toggle process based on scheduled times. Returns True if state changed."""
    now = datetime.now()
    changed = False

    if process.scheduled_start and not process.active and process.scheduled_start <= now:
        process.active = True
        process.scheduled_start = None
        changed = True

    if process.scheduled_end and process.active and process.scheduled_end <= now:
        process.active = False
        process.scheduled_end = None
        changed = True

    if changed:
        db.add(process)
        db.commit()
        db.refresh(process)

    return changed


def _build_status(process: SelectionProcess) -> SelectionProcessStatus:
    is_scheduled = bool(process.scheduled_start or process.scheduled_end)
    return SelectionProcessStatus(
        active=process.active,
        scheduled_start=process.scheduled_start,
        scheduled_end=process.scheduled_end,
        is_scheduled=is_scheduled,
    )


@router.get("/", response_model=SelectionProcessStatus)
def get_selection_process_status(db: Session = Depends(get_session)):
    process = _get_or_create_process(db)
    _check_and_apply_schedule(process, db)
    return _build_status(process)


@router.post("/toggle", response_model=SelectionProcessStatus)
def toggle_selection_process(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)

    process = _get_or_create_process(db)
    process.active = not process.active
    # Clear any pending schedule when manually toggling
    process.scheduled_start = None
    process.scheduled_end = None
    db.add(process)
    db.commit()
    db.refresh(process)

    return _build_status(process)


@router.post("/schedule", response_model=SelectionProcessStatus)
def schedule_selection_process(
    body: ScheduleRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    if body.scheduled_start is None and body.scheduled_end is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes indicar al menos una fecha")

    now = datetime.now()

    start = body.scheduled_start
    end = body.scheduled_end

    if start and start <= now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de inicio debe ser futura")
    if end and end <= now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de fin debe ser futura")
    if start and end and end <= start:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de fin debe ser posterior a la de inicio")

    process = _get_or_create_process(db)
    process.scheduled_start = start
    process.scheduled_end = end
    db.add(process)
    db.commit()
    db.refresh(process)

    return _build_status(process)


@router.delete("/schedule", response_model=SelectionProcessStatus)
def cancel_schedule(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)

    process = _get_or_create_process(db)
    process.scheduled_start = None
    process.scheduled_end = None
    db.add(process)
    db.commit()
    db.refresh(process)

    return _build_status(process)


@router.delete("/end_ERASMUS")
def delete_erasmus(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not any(role.name.lower() in ['admin', 'administrador'] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have no rights to end erasmus")

    try:
        db.exec(delete(FinalList))
        db.exec(delete(Interview))
        db.exec(delete(Calificacion))

        documents = db.exec(select(Document)).all()
        for doc in documents:
            if doc.file_path and os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            db.delete(doc)

        db.exec(delete(Document))
        db.commit()

        return {"message": "All Erasmus data (Final List, Interviews, Qualifications, and Documents) has been successfully deleted."}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while ending ERASMUS: {str(e)}"
        )
