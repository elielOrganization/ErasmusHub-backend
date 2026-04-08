from sqlmodel import SQLModel, Field
from typing import Optional

class SelectionProcess(SQLModel, table=True):
    __tablename__ = "selection_process"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    active: bool = Field(default=False)