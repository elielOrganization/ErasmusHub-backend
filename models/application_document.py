from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class ApplicationDocument(SQLModel, table=True):
    __tablename__ = "application_document"

    application_id: int = Field(foreign_key="application.id", primary_key=True)
    document_id: int = Field(foreign_key="document.id", primary_key=True)
    attached_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
