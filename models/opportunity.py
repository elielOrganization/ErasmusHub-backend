from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .user import User
    from .application import Application


class Opportunity(SQLModel, table=True):
    __tablename__ = "opportunity"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    max_slots: int = Field(default=1)
    filled_slots: int = Field(default=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = Field(default="open")
    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="opportunities_created")
    applications: List["Application"] = Relationship(back_populates="opportunity")
