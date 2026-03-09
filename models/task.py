from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .request import Solicitudes

class Tareas(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(foreign_key="solicitudes.id")
    user_id: int = Field(foreign_key="usuario.id")
    titulo: str
    completed: bool = Field(default=False)
    due_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relación
    solicitud: Optional["Solicitudes"] = Relationship(back_populates="tareas")