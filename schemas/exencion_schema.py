from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExencionRead(BaseModel):
    id: int
    motivo: str
    estado: str
    documento_path: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExencionCreate(BaseModel):
    motivo: str
