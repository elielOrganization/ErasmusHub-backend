from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .practica import Practicas


class DiarioPractica(SQLModel, table=True):
    __tablename__ = "diario_practica"

    id: Optional[int] = Field(default=None, primary_key=True)
    practica_id: int = Field(foreign_key="practicas.id")
    fecha: date
    estado: str = Field(default="pendiente")  # pendiente, completado
    hora_inicio_manana: Optional[str] = None  # e.g. "08:00"
    hora_fin_manana: Optional[str] = None     # e.g. "12:00"
    hora_inicio_tarde: Optional[str] = None   # e.g. "13:00"
    hora_fin_tarde: Optional[str] = None      # e.g. "16:00"
    actividades: Optional[str] = None
    incidencias: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relacion
    practica: Optional["Practicas"] = Relationship(back_populates="diario_entradas")
