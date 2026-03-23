from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import User
    from .opportunity import Opportunity
    from .task import Task


class Application(SQLModel, table=True):
    __tablename__ = "application"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    opportunity_id: int = Field(foreign_key="opportunity.id")
    score: Optional[float] = None
    status: str = Field(default="pending")
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status_changed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Optional["User"] = Relationship(back_populates="applications")
    opportunity: Optional["Opportunity"] = Relationship(back_populates="applications")
    tasks: List["Task"] = Relationship(back_populates="application")
