from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


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


class ApplicationWithStudent(BaseModel):
    application_id: int
    user_id: int
    opportunity_id: int
    opportunity_name: str
    first_name: str
    last_name: str
    email: str
    status: str

    class Config:
        from_attributes = True

class ReassignRequest(BaseModel):
    user_id: int
    new_opportunity_id: int


class ApplicationWithOpportunity(BaseModel):
    id: int
    opportunity_id: int
    status: str
    applied_at: datetime
    opportunity_name: str
    opportunity_description: Optional[str] = None
    opportunity_country: Optional[str] = None
    opportunity_city: Optional[str] = None
    opportunity_start_date: Optional[date] = None
    opportunity_end_date: Optional[date] = None
    opportunity_status: str

    class Config:
        from_attributes = True
