from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .user import User
    from .weekly_schedule import WeeklySchedule
    from .follow_up import FollowUp
    from .daily_log import DailyLog
    from .attendance import Attendance
    from .communication import Communication


class Internship(SQLModel, table=True):
    __tablename__ = "internship"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id")
    company_name: str
    company_tax_id: Optional[str] = None
    company_address: Optional[str] = None
    company_tutor_name: Optional[str] = None
    company_tutor_email: Optional[str] = None
    academic_tutor_name: Optional[str] = None
    start_date: date
    end_date: date
    total_hours: int
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tutor_id: Optional[int] = Field(default=None, foreign_key="user.id")
    co_tutor_id: Optional[int] = Field(default=None, foreign_key="user.id")

    tutor: Optional["User"] = Relationship(
        back_populates="internships_as_tutor",
        sa_relationship_kwargs={"foreign_keys": "[Internship.tutor_id]"},
    )

    # Relationships
    student: Optional["User"] = Relationship(
        back_populates="internships",
        sa_relationship_kwargs={"foreign_keys": "[Internship.student_id]"},
    )
    co_tutor: Optional["User"] = Relationship(
        back_populates="internships_as_cotutor",
        sa_relationship_kwargs={"foreign_keys": "[Internship.co_tutor_id]"},
    )
    schedules: List["WeeklySchedule"] = Relationship(back_populates="internship")
    follow_ups: List["FollowUp"] = Relationship(back_populates="internship")
    daily_logs: List["DailyLog"] = Relationship(back_populates="internship")
    attendances: List["Attendance"] = Relationship(back_populates="internship")
    communications: List["Communication"] = Relationship(back_populates="internship")
