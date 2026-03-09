from sqlmodel import SQLModel, Field
from typing import Optional

class UserRol(SQLModel, table=True):
    __tablename__ = "user_rol"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="usuario.id")
    rol_id: int = Field(foreign_key="roles.id")