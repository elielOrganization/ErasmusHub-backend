from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExemptionCreate(BaseModel):
    reason: str


class ExemptionUpdate(BaseModel):
    status: Optional[str] = None
    document_path: Optional[str] = None


class ExemptionRead(BaseModel):
    id: int
    reason: str
    status: str
    document_path: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None

    class Config:
        from_attributes = True
