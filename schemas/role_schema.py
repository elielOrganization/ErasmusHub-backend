from pydantic import BaseModel
from typing import Optional


class RoleRead(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


