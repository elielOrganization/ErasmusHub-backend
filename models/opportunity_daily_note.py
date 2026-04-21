from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime, timezone


class OpportunityDailyNote(SQLModel, table=True):
    __tablename__ = "opportunity_daily_note"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    opportunity_id: int = Field(foreign_key="opportunity.id")
    date: date
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
