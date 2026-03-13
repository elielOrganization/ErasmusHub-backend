from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- SCHEMA PARA CREAR (Entrada, uso interno/admin) ---
class NotificationCreate(BaseModel):
    user_id: int
    titulo: str
    body: str
    tipo: str


# --- SCHEMA PARA MOSTRAR (Salida) ---
class NotificationRead(BaseModel):
    id: int
    titulo: str
    body: str
    tipo: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- SCHEMA PARA MARCAR COMO LEÍDA ---
class NotificationMarkRead(BaseModel):
    is_read: bool = True
