from pydantic import BaseModel


class LoginRequest(BaseModel):
    rodne_cislo: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
