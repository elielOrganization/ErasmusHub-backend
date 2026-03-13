from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import Usuario


class Exenciones(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    estudiante_id: int = Field(foreign_key="usuario.id")
    motivo: str
    estado: str = Field(default="pendiente")  # pendiente, aprobada, rechazada
    documento_path: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = Field(default=None, foreign_key="usuario.id")

    # Relaciones
    estudiante: Optional["Usuario"] = Relationship(
        back_populates="exenciones",
        sa_relationship_kwargs={"foreign_keys": "[Exenciones.estudiante_id]"}
    )
