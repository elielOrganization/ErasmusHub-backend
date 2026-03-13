from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ============================================================
# CHAT
# ============================================================

class ChatCreate(BaseModel):
    nombre: Optional[str] = None
    tipo: str = "direct"
    participantes: List[int]  # lista de user_ids


class ChatRead(BaseModel):
    id: int
    nombre: Optional[str] = None
    tipo: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# CHAT PARTICIPANT
# ============================================================

class ChatParticipantRead(BaseModel):
    id: int
    chat_id: int
    user_id: int
    rol: str
    joined_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# MESSAGE
# ============================================================

class MessageCreate(BaseModel):
    contenido: str


class MessageRead(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    contenido: str
    leido: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- CHAT CON ÚLTIMO MENSAJE (para lista de conversaciones) ---
class ChatWithLastMessage(ChatRead):
    ultimo_mensaje: Optional[MessageRead] = None
    no_leidos: int = 0
