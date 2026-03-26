from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


class Calificacion(SQLModel, table=True):
    __tablename__ = "calification"

    id: Optional[int] = Field(default=None, primary_key=True)
    interview: float = Field(default=0.0)
    grade_certificate: float = Field(default=0.0)
    motivation_letter: float = Field(default=0.0)
    language_certificate: float = Field(default=0.0)
    disability_certificate: float = Field(default=0.0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = Field(default=None, foreign_key="user.id")
