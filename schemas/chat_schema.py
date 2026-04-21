from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    sender_name: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRead(BaseModel):
    id: int
    opportunity_id: int
    opportunity_name: str
    student_id: int
    student_name: str
    teachers_names: str
    unread_count: int = 0
    last_message: Optional[MessageRead] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TeacherAssign(BaseModel):
    teacher_id: int


class TeacherInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True
