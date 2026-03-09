from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING # TYPE_CHECKING es la clave
from datetime import datetime, timezone

# Esto permite que los editores de código reconozcan el tipo 'Usuario' 
# para el autocompletado, pero NO se ejecuta en tiempo de ejecución, 
# evitando el error circular.
if TYPE_CHECKING:
    from .user import Usuario 

class Notificaciones(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Importante: foreign_key usa el nombre de la TABLA en minúsculas (usualmente)
    user_id: int = Field(foreign_key="usuario.id") 
    titulo: str
    body: str
    tipo: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # RELACIÓN: Usamos "Usuario" como string
    usuario: Optional["Usuario"] = Relationship(back_populates="notificaciones")