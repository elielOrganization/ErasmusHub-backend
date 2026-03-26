from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class DocumentCreate(BaseModel):
    name: str
    document_type: Optional[str] = None


class DocumentRead(BaseModel):
    id: int
    user_id: int
    name: str
    document_type: Optional[str] = None
    file_path: Optional[str] = None
    state: Literal["pending", "approved", "rejected"]
    uploaded_at: datetime

    class Config:
        from_attributes = True
