from sqlmodel import SQLModel, Field
from typing import Optional


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)
