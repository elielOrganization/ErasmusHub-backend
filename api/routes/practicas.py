from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime, timezone

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.internship import Internship
from models.weekly_schedule import WeeklySchedule
from models.follow_up import FollowUp
from models.daily_log import DailyLog
from models.attendance import Attendance
from models.communication import Communication
from schemas.practica_schema import (
    InternshipList, InternshipDetail, ScheduleRead,
    FollowUpRead, FollowUpSubmit,
    DailyLogRead, DailyLogCreate, DailyLogUpdate,
    AttendanceRead,
    CommunicationRead, CommunicationCreate,
)
from schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/internships", tags=["Internships"])


@router.get("/me", response_model=PaginatedResponse[InternshipList])
def list_my_internships(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    query = select(Internship).where(Internship.student_id == current_user.id)
    if search:
        query = query.where(Internship.company_name.ilike(f"%{search}%"))

    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(query.offset((page - 1) * page_size).limit(page_size)).all()

    return PaginatedResponse(
        items=[InternshipList.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{internship_id}", response_model=InternshipDetail)
def get_internship_detail(
    internship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    schedules = db.exec(
        select(WeeklySchedule).where(WeeklySchedule.internship_id == internship_id)
    ).all()

    return InternshipDetail(
        id=internship.id,
        student_first_name=current_user.first_name,
        student_last_name=current_user.last_name,
        student_email=current_user.email,
        company_name=internship.company_name,
        company_tax_id=internship.company_tax_id,
        company_address=internship.company_address,
        company_tutor_name=internship.company_tutor_name,
        company_tutor_email=internship.company_tutor_email,
        academic_tutor_name=internship.academic_tutor_name,
        start_date=internship.start_date,
        end_date=internship.end_date,
        total_hours=internship.total_hours,
        status=internship.status,
        schedules=[ScheduleRead.model_validate(s) for s in schedules],
    )


# --- FOLLOW-UPS ---

@router.get("/{internship_id}/follow-ups", response_model=list[FollowUpRead])
def list_follow_ups(
    internship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    items = db.exec(
        select(FollowUp)
        .where(FollowUp.internship_id == internship_id)
        .order_by(FollowUp.scheduled_date)
    ).all()
    return [FollowUpRead.model_validate(f) for f in items]


@router.post("/{internship_id}/follow-ups/{follow_up_id}/complete", response_model=FollowUpRead)
def complete_follow_up(
    internship_id: int,
    follow_up_id: int,
    data: FollowUpSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    follow_up = db.get(FollowUp, follow_up_id)
    if not follow_up or follow_up.internship_id != internship_id:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    follow_up.completed = True
    follow_up.completed_at = datetime.now(timezone.utc)
    follow_up.answers = data.answers
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return FollowUpRead.model_validate(follow_up)


# --- DAILY LOG ---

@router.get("/{internship_id}/daily-logs", response_model=PaginatedResponse[DailyLogRead])
def list_daily_logs(
    internship_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    query = select(DailyLog).where(DailyLog.internship_id == internship_id)
    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    items = db.exec(
        query.order_by(DailyLog.date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedResponse(
        items=[DailyLogRead.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{internship_id}/daily-logs", response_model=DailyLogRead)
def create_or_update_daily_log(
    internship_id: int,
    data: DailyLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    existing = db.exec(
        select(DailyLog)
        .where(DailyLog.internship_id == internship_id)
        .where(DailyLog.date == data.date)
    ).first()

    if existing:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        existing.status = "completed"
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return DailyLogRead.model_validate(existing)

    entry = DailyLog(
        internship_id=internship_id,
        status="completed",
        **data.model_dump(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return DailyLogRead.model_validate(entry)


# --- ATTENDANCE (CALENDAR) ---

@router.get("/{internship_id}/attendance", response_model=list[AttendanceRead])
def list_attendance(
    internship_id: int,
    month: Optional[str] = Query(None, description="YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    query = select(Attendance).where(Attendance.internship_id == internship_id)
    if month:
        query = query.where(
            func.to_char(Attendance.date, "YYYY-MM") == month
        )
    items = db.exec(query.order_by(Attendance.date)).all()
    return [AttendanceRead.model_validate(a) for a in items]


# --- COMMUNICATIONS ---

@router.get("/{internship_id}/communications", response_model=list[CommunicationRead])
def list_communications(
    internship_id: int,
    recipient_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    query = select(Communication).where(Communication.internship_id == internship_id)
    if recipient_type:
        query = query.where(Communication.recipient_type == recipient_type)
    items = db.exec(query.order_by(Communication.created_at.desc())).all()
    return [CommunicationRead.model_validate(c) for c in items]


@router.post("/{internship_id}/communications", response_model=CommunicationRead)
def create_communication(
    internship_id: int,
    data: CommunicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    internship = db.get(Internship, internship_id)
    if not internship or internship.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Internship not found")

    com = Communication(
        internship_id=internship_id,
        sender_id=current_user.id,
        **data.model_dump(),
    )
    db.add(com)
    db.commit()
    db.refresh(com)
    return CommunicationRead.model_validate(com)
