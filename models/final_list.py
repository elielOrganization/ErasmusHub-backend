from sqlmodel import SQLModel, Field
from typing import Optional

class FinalList(SQLModel, table=True):
    __tablename__ = "final_list"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    first_name: str
    last_name: str
    year: Optional[str] = None
    final_grade: float
    
    published_by: int = Field(foreign_key="user.id")