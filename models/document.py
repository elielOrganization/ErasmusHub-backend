from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from enum import Enum


class DocumentState(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class DocumentReviewUpdate(BaseModel):
    state: DocumentState
    grade: Optional[float] = None

class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    document_type: Optional[str] = None
    file_path: Optional[str] = None
    state: DocumentState = Field(default=DocumentState.pending)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    calificable: bool = False
    grade: Optional[float]
