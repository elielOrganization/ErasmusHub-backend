from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .internship import Internship


class DailyLog(SQLModel, table=True):
    __tablename__ = "daily_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    internship_id: int = Field(foreign_key="internship.id")
    date: date
    status: str = Field(default="pending")
    morning_start: Optional[str] = None
    morning_end: Optional[str] = None
    afternoon_start: Optional[str] = None
    afternoon_end: Optional[str] = None
    activities: Optional[str] = None
    incidents: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    internship: Optional["Internship"] = Relationship(back_populates="daily_logs")
