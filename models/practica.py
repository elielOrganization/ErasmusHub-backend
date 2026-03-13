from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime, timezone

if TYPE_CHECKING:
    from .user import Usuario
    from .horario_semanal import HorarioSemanal
    from .seguimiento import Seguimientos
    from .diario_practica import DiarioPractica
    from .asistencia import Asistencia
    from .comunicacion import Comunicaciones


class Practicas(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    estudiante_id: int = Field(foreign_key="usuario.id")
    empresa_nombre: str
    empresa_cif: Optional[str] = None
    empresa_direccion: Optional[str] = None
    tutor_empresa_nombre: Optional[str] = None
    tutor_empresa_email: Optional[str] = None
    tutor_educativo_nombre: Optional[str] = None
    cotutor_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    fecha_inicio: date
    fecha_fin: date
    horas_totales: int
    estado: str = Field(default="activa")  # activa, finalizada, cancelada
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relaciones
    estudiante: Optional["Usuario"] = Relationship(
        back_populates="practicas",
        sa_relationship_kwargs={"foreign_keys": "[Practicas.estudiante_id]"}
    )
    cotutor: Optional["Usuario"] = Relationship(
        back_populates="practicas_como_cotutor",
        sa_relationship_kwargs={"foreign_keys": "[Practicas.cotutor_id]"}
    )
    horarios: List["HorarioSemanal"] = Relationship(back_populates="practica")
    seguimientos: List["Seguimientos"] = Relationship(back_populates="practica")
    diario_entradas: List["DiarioPractica"] = Relationship(back_populates="practica")
    asistencias: List["Asistencia"] = Relationship(back_populates="practica")
    comunicaciones: List["Comunicaciones"] = Relationship(back_populates="practica")
