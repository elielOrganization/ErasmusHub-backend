from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .user_role import UserRole


class Role(SQLModel, table=True):
    __tablename__ = "role"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(unique=True)
    description: Optional[str] = None

    # Relationship
    users: List["User"] = Relationship(back_populates="roles", link_model="UserRole")
