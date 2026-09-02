from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(50), default="Student")  # Student, Professional, Other
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    speaking_sessions = relationship("SpeakingSession", back_populates="user", cascade="all, delete-orphan")
    writing_sessions = relationship("WritingSession", back_populates="user", cascade="all, delete-orphan")
    listening_sessions = relationship("ListeningSession", back_populates="user", cascade="all, delete-orphan")
    vocabulary_items = relationship("VocabularyItem", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    profession = Column(String(100), default="General")  # Software Developer, Data Scientist, HR, Sales, etc.
    target_level = Column(String(50), default="Intermediate")  # Beginner, Basic, Intermediate, Advanced, Professional
    primary_goal = Column(String(100), default="General Improvement")
    practice_duration = Column(Integer, default=15)  # minutes per day
    baseline_score = Column(Integer, default=50)

    user = relationship("User", back_populates="profile")
