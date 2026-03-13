from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List


# --- SCHEMA BASE (Campos comunes) ---
class UserBase(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str


# --- SCHEMA PARA CREAR (Entrada) ---
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Contraseña en texto plano")
    rodne_cislo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    es_menor: bool = False
    direccion: Optional[str] = None
    telefono: Optional[str] = None


# --- SCHEMA PARA ACTUALIZAR (Entrada opcional) ---
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    password: Optional[str] = None
    rodne_cislo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    es_menor: Optional[bool] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None


# --- SCHEMA PARA MOSTRAR (Salida pública) ---
class UserPublic(UserBase):
    id: int
    rodne_cislo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    es_menor: bool = False
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    created_at: datetime
    roles: List[str] = []

    class Config:
        from_attributes = True