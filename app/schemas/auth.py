from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    user_type: Optional[str] = "Student"
    profession: Optional[str] = "General"
    primary_goal: Optional[str] = "General Improvement"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
