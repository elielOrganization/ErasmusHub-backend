from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .internship import Internship


class FollowUp(SQLModel, table=True):
    __tablename__ = "follow_up"

    id: Optional[int] = Field(default=None, primary_key=True)
    internship_id: int = Field(foreign_key="internship.id")
    type: str  # initial, intermediate, final
    scheduled_date: date
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    answers: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    internship: Optional["Internship"] = Relationship(back_populates="follow_ups")
