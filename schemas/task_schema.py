from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- SCHEMA PARA CREAR (Entrada) ---
class TaskCreate(BaseModel):
    titulo: str
    app_id: Optional[int] = None
    due_date: Optional[datetime] = None


# --- SCHEMA PARA ACTUALIZAR (Entrada opcional) ---
class TaskUpdate(BaseModel):
    titulo: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


# --- SCHEMA PARA MOSTRAR (Salida) ---
class TaskRead(BaseModel):
    id: int
    user_id: int
    app_id: Optional[int] = None
    titulo: str
    completed: bool
    due_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
