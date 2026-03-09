from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import Usuario
    from .request import Solicitudes

class Oportunidades(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descripcion: str
    pais: str
    ciudad: str
    estado: str
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int = Field(foreign_key="usuario.id")

    # Relaciones
    creador: Optional["Usuario"] = Relationship(back_populates="oportunidades_creadas")
    solicitudes: List["Solicitudes"] = Relationship(back_populates="oportunidad")