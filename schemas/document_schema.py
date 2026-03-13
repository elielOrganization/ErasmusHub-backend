from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentCreate(BaseModel):
    name: str
    document_type: Optional[str] = None
    application_id: Optional[int] = None


class DocumentRead(BaseModel):
    id: int
    user_id: int
    application_id: Optional[int] = None
    name: str
    document_type: Optional[str] = None
    file_path: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True
