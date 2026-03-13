from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExencionCreate(BaseModel):
    motivo: str


class ExencionUpdate(BaseModel):
    estado: Optional[str] = None
    documento_path: Optional[str] = None


class ExencionRead(BaseModel):
    id: int
    motivo: str
    estado: str
    documento_path: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None

    class Config:
        from_attributes = True
