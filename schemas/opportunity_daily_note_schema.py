from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class DailyNoteUpsert(BaseModel):
    opportunity_id: int
    date: date
    notes: str


class DailyNoteRead(BaseModel):
    id: int
    user_id: int
    opportunity_id: int
    date: date
    notes: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True
