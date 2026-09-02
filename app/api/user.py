from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Profile
from app.schemas.user import ProfileOut, ProfileBase
from app.api.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["User Profile"])

@router.get("", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        profile = Profile(user_id=current_user.user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("", response_model=ProfileOut)
def update_profile(
    profile_in: ProfileBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        profile = Profile(user_id=current_user.user_id)
        db.add(profile)
    
    for key, value in profile_in.dict(exclude_unset=True).items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile
