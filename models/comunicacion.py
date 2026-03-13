from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .practica import Practicas
    from .user import Usuario


class Comunicaciones(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    practica_id: int = Field(foreign_key="practicas.id")
    emisor_id: int = Field(foreign_key="usuario.id")
    destinatario_tipo: str  # tutor_empresa, cotutor
    tipo: str  # mensaje, consulta, incidencia
    asunto: str
    mensaje: str
    leido: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relaciones
    practica: Optional["Practicas"] = Relationship(back_populates="comunicaciones")
    emisor: Optional["Usuario"] = Relationship(back_populates="comunicaciones_enviadas")
