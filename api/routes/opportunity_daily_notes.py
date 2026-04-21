from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone, date as date_type

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.opportunity_daily_note import OpportunityDailyNote
from schemas.opportunity_daily_note_schema import DailyNoteUpsert, DailyNoteRead

router = APIRouter(prefix="/opportunity-daily-notes", tags=["Opportunity Daily Notes"])


@router.get("/", response_model=list[DailyNoteRead])
def get_notes(
    opportunity_id: int,
    student_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Return daily notes for a given opportunity.
    - Student: returns their own notes (student_id ignored).
    - Tutor: pass student_id to read a student's notes; only allowed if
      this user is the assigned tutor for that student/opportunity pair.
    """
    from models.application import Application

    if student_id is not None and student_id != current_user.id:
        # Verify the caller is the tutor assigned to this student+opportunity
        assignment = db.exec(
            select(Application)
            .where(Application.user_id == student_id)
            .where(Application.opportunity_id == opportunity_id)
            .where(Application.tutor_id == current_user.id)
        ).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso al diario de este alumno.",
            )
        target_user_id = student_id
    else:
        target_user_id = current_user.id

    notes = db.exec(
        select(OpportunityDailyNote)
        .where(OpportunityDailyNote.user_id == target_user_id)
        .where(OpportunityDailyNote.opportunity_id == opportunity_id)
        .order_by(OpportunityDailyNote.date)
    ).all()
    return notes


@router.post("/", response_model=DailyNoteRead)
def upsert_note(
    data: DailyNoteUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Create or update the note for a specific day. One note per user/opportunity/date."""
    # No se permiten notas para fechas futuras (validación en servidor)
    if data.date > date_type.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden registrar notas para fechas futuras.",
        )

    existing = db.exec(
        select(OpportunityDailyNote)
        .where(OpportunityDailyNote.user_id == current_user.id)
        .where(OpportunityDailyNote.opportunity_id == data.opportunity_id)
        .where(OpportunityDailyNote.date == data.date)
    ).first()

    now = datetime.now(timezone.utc)

    if existing:
        existing.notes = data.notes
        existing.updated_at = now
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    note = OpportunityDailyNote(
        user_id=current_user.id,
        opportunity_id=data.opportunity_id,
        date=data.date,
        notes=data.notes,
        updated_at=now,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
