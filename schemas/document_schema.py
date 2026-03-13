from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- SCHEMA PARA SUBIR (Entrada) ---
class DocumentCreate(BaseModel):
    nombre: str
    tipo_documento: Optional[str] = None
    application_id: Optional[int] = None


# --- SCHEMA PARA MOSTRAR (Salida) ---
class DocumentRead(BaseModel):
    id: int
    user_id: int
    application_id: Optional[int] = None
    nombre: str
    tipo_documento: Optional[str] = None
    file_path: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True
