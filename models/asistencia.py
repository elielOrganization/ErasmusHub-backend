from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from .practica import Practicas


class Asistencia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    practica_id: int = Field(foreign_key="practicas.id")
    fecha: date
    tipo: str  # asistencia, falta_justificada, falta_injustificada, festivo
    hora_inicio: Optional[str] = None  # e.g. "08:00"
    hora_fin: Optional[str] = None     # e.g. "16:00"
    estado: str = Field(default="pendiente")  # pendiente, completado
    notas: Optional[str] = None

    # Relacion
    practica: Optional["Practicas"] = Relationship(back_populates="asistencias")
