from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- SCHEMA PARA CREAR (Entrada) ---
class ApplicationCreate(BaseModel):
    oportunidades_id: int


# --- SCHEMA PARA ACTUALIZAR (Entrada, uso coordinador) ---
class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    score: Optional[float] = None


# --- SCHEMA PARA LISTAR ---
class ApplicationList(BaseModel):
    id: int
    oportunidades_id: int
    status: str
    score: Optional[float] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


# --- SCHEMA DETALLE ---
class ApplicationDetail(ApplicationList):
    estudiante_id: int
    update_at: datetime

    class Config:
        from_attributes = True
