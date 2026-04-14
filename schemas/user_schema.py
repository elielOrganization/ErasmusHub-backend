from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List
from models.role import Role


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):

    password: str = Field(..., min_length=8)
    rodne_cislo: Optional[str] = None
    birth_date: Optional[date] = None
    is_minor: bool = False
    address: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    role_id: Optional[int] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    rodne_cislo: Optional[str] = None
    birth_date: Optional[date] = None
    is_minor: Optional[bool] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    year: Optional[str] = None
    grade: Optional[float] = None


class UserPublic(UserBase):
    id: int
    rodne_cislo: Optional[str] = None
    birth_date: Optional[date] = None
    is_minor: bool = False
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    role: Optional[Role] = None
    year: Optional[str] = None
    grade: Optional[float] = None
    final_grade: Optional[float] = None

    class Config:
        from_attributes = True
