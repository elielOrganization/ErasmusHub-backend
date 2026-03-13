from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .practica import Practicas


class HorarioSemanal(SQLModel, table=True):
    __tablename__ = "horario_semanal"

    id: Optional[int] = Field(default=None, primary_key=True)
    practica_id: int = Field(foreign_key="practicas.id")
    dia_semana: str  # lunes, martes, miercoles, jueves, viernes
    horario_manana: Optional[str] = None  # e.g. "De 08:00 a 12:00"
    horario_tarde: Optional[str] = None   # e.g. "De 13:00 a 16:00"

    # Relacion
    practica: Optional["Practicas"] = Relationship(back_populates="horarios")
