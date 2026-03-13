from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .practica import Practicas


class Seguimientos(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    practica_id: int = Field(foreign_key="practicas.id")
    tipo: str  # inicial, intermedio, final
    fecha_programada: date
    completado: bool = Field(default=False)
    fecha_completado: Optional[datetime] = None
    respuestas: Optional[str] = None  # JSON string for questionnaire answers
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relacion
    practica: Optional["Practicas"] = Relationship(back_populates="seguimientos")
