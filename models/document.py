from sqlmodel import SQLModel, Field
from typing import Optional, Literal
from datetime import datetime, timezone


class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    document_type: Optional[str] = None
    file_path: Optional[str] = None
    state: Literal["pending", "approved", "rejected"] = Field(default="pending")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
