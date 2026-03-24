from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: int
    message_key: str   # e.g. "app_accepted", "task_due_soon"
    params: Optional[str] = None  # JSON string with template variables
    type: str


class NotificationRead(BaseModel):
    id: int
    message_key: str
    params: Optional[str] = None
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    is_read: bool = True
