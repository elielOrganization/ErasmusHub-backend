from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

from .user_role import UserRole

if TYPE_CHECKING:
    from .user import User

class Role(SQLModel, table=True):
    __tablename__ = "role"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    # Relationship
    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole, 
    )