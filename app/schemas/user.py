from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class ProfileBase(BaseModel):
    profession: Optional[str] = "General"
    target_level: Optional[str] = "Intermediate"
    primary_goal: Optional[str] = "General Improvement"
    practice_duration: Optional[int] = 15
    baseline_score: Optional[int] = 50

class ProfileCreate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    profile_id: int
    user_id: int

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    user_type: str
    created_at: datetime
    profile: Optional[ProfileOut] = None

    class Config:
        from_attributes = True
