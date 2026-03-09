from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .request import Solicitudes

class Documentos(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(foreign_key="solicitudes.id") # app_id en tu diagrama apunta a solicitudes
    doc_type: str
    file_path: str
    status: str
    comentarios: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None

    # Relación
    solicitud: Optional["Solicitudes"] = Relationship(back_populates="documentos")