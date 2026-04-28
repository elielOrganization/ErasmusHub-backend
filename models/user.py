from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime, timezone

# Import UserRole directly to fix the inspection error
from .user_role import UserRole

if TYPE_CHECKING:
    from .role import Role
    from .opportunity import Opportunity
    from .application import Application
    from .notification import Notification
    from .interview import Interview
    from .chat import Chat, ChatMessage


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    rodne_cislo: Optional[str] = None
    rodne_cislo_hash: Optional[str] = Field(default=None, unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    is_minor: bool = Field(default=False)
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    year: Optional[str] = None
    final_grade: Optional[float] = None

    # Relationships
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole,
    )
    
    opportunities_created: List["Opportunity"] = Relationship(back_populates="creator")
    applications: List["Application"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Application.user_id]"},
    )
    tutored_applications: List["Application"] = Relationship(
        back_populates="tutor",
        sa_relationship_kwargs={"foreign_keys": "[Application.tutor_id]"},
    )
    notifications: List["Notification"] = Relationship(back_populates="user")

    interviews: List["Interview"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "[Interview.user_id]"}
    )
    
    interviews_reviewed: List["Interview"] = Relationship(
        back_populates="reviewer",
        sa_relationship_kwargs={"foreign_keys": "Interview.reviewed_by"}
    )

    chats_as_student: List["Chat"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "[Chat.student_id]"},
    )
    chat_messages_sent: List["ChatMessage"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "[ChatMessage.sender_id]"},
    )