from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import User
    from .opportunity import Opportunity


class Application(SQLModel, table=True):
    __tablename__ = "application"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    opportunity_id: int = Field(foreign_key="opportunity.id")
    tutor_id: Optional[int] = Field(default=None, foreign_key="user.id")
    score: Optional[float] = None
    status: str = Field(default="pending")
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status_changed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="applications",
        sa_relationship_kwargs={"foreign_keys": "[Application.user_id]"},
    )
    tutor: Optional["User"] = Relationship(
        back_populates="tutored_applications",
        sa_relationship_kwargs={"foreign_keys": "[Application.tutor_id]"},
    )
    opportunity: Optional["Opportunity"] = Relationship(back_populates="applications")
