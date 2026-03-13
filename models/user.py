from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .role import Role
    from .user_role import UserRole
    from .opportunity import Opportunity
    from .application import Application
    from .notification import Notification
    from .internship import Internship
    from .communication import Communication
    from .exemption import Exemption


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    first_name: str
    last_name: str
    rodne_cislo: Optional[str] = Field(default=None, index=True)
    birth_date: Optional[date] = None
    is_minor: bool = Field(default=False)
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model="UserRole",
    )
    opportunities_created: List["Opportunity"] = Relationship(back_populates="creator")
    applications: List["Application"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    internships: List["Internship"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "[Internship.student_id]"},
    )
    internships_as_cotutor: List["Internship"] = Relationship(
        back_populates="co_tutor",
        sa_relationship_kwargs={"foreign_keys": "[Internship.co_tutor_id]"},
    )
    communications_sent: List["Communication"] = Relationship(back_populates="sender")
    exemptions: List["Exemption"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "[Exemption.student_id]"},
    )
