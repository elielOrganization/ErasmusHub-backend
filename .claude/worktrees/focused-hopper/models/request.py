from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import Usuario
    from .opportunity import Oportunidades
    from .document import Documentos
    from .task import Tareas

class Solicitudes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    score: Optional[float] = 0.0
    status: str
    estudiante_id: int = Field(foreign_key="usuario.id")
    oportunidades_id: int = Field(foreign_key="oportunidades.id")
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relaciones
    estudiante: Optional["Usuario"] = Relationship(back_populates="solicitudes")
    oportunidad: Optional["Oportunidades"] = Relationship(back_populates="solicitudes")
    documentos: List["Documentos"] = Relationship(back_populates="solicitud")
    tareas: List["Tareas"] = Relationship(back_populates="solicitud")