from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# --- SCHEMA BASE (Campos comunes) ---
class UserBase(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str

# --- SCHEMA PARA CREAR (Entrada) ---
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Contraseña en texto plano")

# --- SCHEMA PARA ACTUALIZAR (Entrada opcional) ---
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    password: Optional[str] = None

# --- SCHEMA PARA MOSTRAR (Salida pública) ---
class UserPublic(UserBase):
    id: int
    created_at: datetime
    # updated_at: datetime # Opcional, si quieres mostrarlo

    class Config:
        # Esto permite que Pydantic lea datos de objetos de SQLModel/SQLAlchemy
        from_attributes = True

class UserLogIn(UserBase):
    email: str
    password: str
    