from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum

if TYPE_CHECKING:
    from .user import User

class InterviewStatus(str, Enum):
    pending = "pending"
    passed = "passed"
    rejected = "rejected"

class Interview(SQLModel, table=True):
    __tablename__ = "interview"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: int = Field(foreign_key="user.id", index=True)
    student: Optional["User"] = Relationship(
        back_populates="interviews",
        sa_relationship_kwargs={"foreign_keys": "[Interview.user_id]"}
    )


    grade: Optional[float] = Field(default=None)
    status: InterviewStatus = Field(default=InterviewStatus.pending)
    rejection_reason: Optional[str] = None

    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewer: Optional["User"] = Relationship(
        back_populates="interviews_reviewed",
        sa_relationship_kwargs={"foreign_keys": "Interview.reviewed_by"}
    )
    
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))