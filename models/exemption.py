from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import User


class Exemption(SQLModel, table=True):
    __tablename__ = "exemption"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id")
    reason: str
    status: str = Field(default="pending")
    document_path: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")

    # Relationship
    student: Optional["User"] = Relationship(
        back_populates="exemptions",
        sa_relationship_kwargs={"foreign_keys": "[Exemption.student_id]"},
    )
