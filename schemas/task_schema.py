from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    application_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskRead(BaseModel):
    id: int
    user_id: int
    application_id: Optional[int] = None
    title: str
    completed: bool
    due_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
