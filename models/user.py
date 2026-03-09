from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from .rol import Roles
from .user_rol import UserRol

if TYPE_CHECKING:
    from .opportunity import Oportunidades
    from .request import Solicitudes
    from .notifications import Notificaciones

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    nombre: str
    apellidos: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relaciones
    roles: List[Roles] = Relationship(back_populates="usuarios", link_model=UserRol)
    oportunidades_creadas: List["Oportunidades"] = Relationship(back_populates="creador")
    solicitudes: List["Solicitudes"] = Relationship(back_populates="estudiante")
    notificaciones: List["Notificaciones"] = Relationship(back_populates="usuario")