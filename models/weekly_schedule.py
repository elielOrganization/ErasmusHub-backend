from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .internship import Internship


class WeeklySchedule(SQLModel, table=True):
    __tablename__ = "weekly_schedule"

    id: Optional[int] = Field(default=None, primary_key=True)
    internship_id: int = Field(foreign_key="internship.id")
    weekday: str
    morning_hours: Optional[str] = None
    afternoon_hours: Optional[str] = None

    # Relationship
    internship: Optional["Internship"] = Relationship(back_populates="schedules")
