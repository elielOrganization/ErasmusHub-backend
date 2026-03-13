from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatCreate(BaseModel):
    name: Optional[str] = None
    type: str = "direct"
    participants: List[int]


class ChatRead(BaseModel):
    id: int
    name: Optional[str] = None
    type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatParticipantRead(BaseModel):
    id: int
    chat_id: int
    user_id: int
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatWithLastMessage(ChatRead):
    last_message: Optional[MessageRead] = None
    unread_count: int = 0
