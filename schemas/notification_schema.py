from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationBroadcast(BaseModel):
    message_key: str
    type: str
    params: Optional[str] = None


class NotificationRead(BaseModel):
    id: int
    message_key: str
    params: Optional[str] = None
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


