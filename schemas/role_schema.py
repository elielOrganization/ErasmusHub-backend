from pydantic import BaseModel
from typing import Optional


class RoleRead(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    user_id: int
    role_id: int


class UserRoleRemove(BaseModel):
    user_id: int
    role_id: int
