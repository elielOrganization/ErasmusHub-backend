from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationCreate(BaseModel):
    opportunity_id: int
    user_id: Optional[int] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    score: Optional[float] = None


class ApplicationList(BaseModel):
    id: int
    opportunity_id: int
    status: str
    score: Optional[float] = None
    applied_at: datetime

    class Config:
        from_attributes = True


class ApplicationDetail(ApplicationList):
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True
