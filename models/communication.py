from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .internship import Internship
    from .user import User


class Communication(SQLModel, table=True):
    __tablename__ = "communication"

    id: Optional[int] = Field(default=None, primary_key=True)
    internship_id: int = Field(foreign_key="internship.id")
    sender_id: int = Field(foreign_key="user.id")
    recipient_type: str  # company_tutor, co_tutor
    type: str  # message, query, incident
    subject: str
    body: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    internship: Optional["Internship"] = Relationship(back_populates="communications")
    sender: Optional["User"] = Relationship(back_populates="communications_sent")
