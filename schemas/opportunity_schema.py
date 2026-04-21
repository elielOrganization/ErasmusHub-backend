from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class OpportunityBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    max_slots: int = 1
    status: str = "open"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    max_slots: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class OpportunityList(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    max_slots: int
    filled_slots: int
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OpportunityDetail(OpportunityList):
    creator_id: Optional[int] = None
    responsible_teacher_id: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class OpportunityDelete(BaseModel):
    id: int
    name: str
    description: Optional[str] = None