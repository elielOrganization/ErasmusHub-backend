from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.interview import Interview
from models.role import Role
from models.user_role import UserRole
from services.notification_service import create_notification

router = APIRouter(prefix="/interviews", tags=["Interviews"])

REVIEWER_ROLE_KEYWORDS = ("admin", "teacher", "profesor", "professor", "coordinator", "coordinador")


def _is_reviewer(role_name: str) -> bool:
    return any(r in role_name.lower() for r in REVIEWER_ROLE_KEYWORDS)


class InterviewUpdate(BaseModel):
    grade: Optional[float] = None
    status: Optional[str] = None        # "rejected"
    rejection_reason: Optional[str] = None


@router.patch("/{user_id}")
def update_interview(
    user_id: int,
    data: InterviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Teacher grades or rejects a student's interview."""
    role_id = db.exec(select(UserRole.role_id).where(UserRole.user_id == current_user.id)).first()
    role_name = db.exec(select(Role.name).where(Role.id == role_id)).first() or ""
    if not _is_reviewer(role_name):
        raise HTTPException(status_code=403, detail="Only teachers and administrators can manage interviews.")

    student = db.get(User, user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    interview = db.exec(select(Interview).where(Interview.user_id == user_id)).first()
    if not interview:
        interview = Interview(user_id=user_id)
        db.add(interview)

    if data.status == "rejected":
        if not data.rejection_reason or not data.rejection_reason.strip():
            raise HTTPException(status_code=400, detail="A rejection reason is required.")
        interview.status = "rejected"
        interview.rejection_reason = data.rejection_reason.strip()
        interview.grade = None
        interview.reviewed_by = current_user.id
        interview.reviewed_at = datetime.now(timezone.utc)
        db.add(interview)
        db.commit()
        db.refresh(interview)

        create_notification(
            db=db,
            user_id=user_id,
            message_key="interview_rejected",
            notif_type="application_update",
            params={"reason": interview.rejection_reason},
        )

    elif data.grade is not None:
        if data.grade < 0 or data.grade > 10:
            raise HTTPException(status_code=400, detail="Grade must be between 0 and 10.")
        interview.grade = data.grade
        interview.status = "passed"
        interview.rejection_reason = None
        interview.reviewed_by = current_user.id
        interview.reviewed_at = datetime.now(timezone.utc)
        db.add(interview)
        db.commit()
        db.refresh(interview)

        create_notification(
            db=db,
            user_id=user_id,
            message_key="interview_passed",
            notif_type="application_update",
            params={"grade": str(interview.grade)},
        )

    elif data.status == "pending":
        interview.status = "pending"
        interview.grade = None
        interview.rejection_reason = None
        interview.reviewed_by = current_user.id
        interview.reviewed_at = datetime.now(timezone.utc)
        db.add(interview)
        db.commit()
        db.refresh(interview)

        create_notification(
            db=db,
            user_id=user_id,
            message_key="interview_readmitted",
            notif_type="application_update",
            params={},
        )

    else:
        raise HTTPException(status_code=400, detail="You must provide a grade or reject the student.")

    return {
        "user_id": user_id,
        "grade": interview.grade,
        "status": interview.status,
        "rejection_reason": interview.rejection_reason,
    }
