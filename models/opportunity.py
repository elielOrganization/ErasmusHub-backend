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
    address: Optional[str] = None
    institution: Optional[str] = None
    duration_days: Optional[int] = None
    max_slots: int = Field(default=1)
    filled_slots: int = Field(default=0)
    type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="open")
    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    responsible_teacher_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    creator: Optional["User"] = Relationship(
        back_populates="opportunities_created",
        sa_relationship_kwargs={"foreign_keys": "[Opportunity.creator_id]"},
    )
    responsible_teacher: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Opportunity.responsible_teacher_id]"},
    )
    applications: List["Application"] = Relationship(back_populates="opportunity")
