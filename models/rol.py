from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from .user_rol import UserRol

if TYPE_CHECKING:
    from .user import Usuario

class Roles(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    rol: str  # coordinador, profesor, estudiante, administrador
    
    # Relación inversa con usuarios a través de la tabla intermedia
    usuarios: List["Usuario"] = Relationship(back_populates="roles", link_model=UserRol)