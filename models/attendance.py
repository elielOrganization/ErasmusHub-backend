from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from .internship import Internship


class Attendance(SQLModel, table=True):
    __tablename__ = "attendance"

    id: Optional[int] = Field(default=None, primary_key=True)
    internship_id: int = Field(foreign_key="internship.id")
    date: date
    type: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: str = Field(default="pending")
    notes: Optional[str] = None

    # Relationship
    internship: Optional["Internship"] = Relationship(back_populates="attendances")
