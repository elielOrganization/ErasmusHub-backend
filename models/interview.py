from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


class Interview(SQLModel, table=True):
    __tablename__ = "interview"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    grade: Optional[float] = None
    status: str = Field(default="pending")  # pending | passed | rejected
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
