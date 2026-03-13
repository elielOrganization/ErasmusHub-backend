from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# --- SCHEMA BASE ---
class OpportunityBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    estado: str = "open"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# --- SCHEMA PARA CREAR (Entrada) ---
class OpportunityCreate(OpportunityBase):
    pass


# --- SCHEMA PARA ACTUALIZAR (Entrada opcional) ---
class OpportunityUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# --- SCHEMA PARA LISTAR ---
class OpportunityList(BaseModel):
    id: int
    titulo: str
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    estado: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- SCHEMA DETALLE ---
class OpportunityDetail(OpportunityList):
    descripcion: Optional[str] = None
    created_by: int
    update_at: datetime

    class Config:
        from_attributes = True
