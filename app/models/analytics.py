from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Progress(Base):
    __tablename__ = "progress"

    progress_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    component_scores = Column(JSON, default=dict)  # {"fluency": 75, "grammar": 80, ...}
    overall_score = Column(Float, default=0.0)
    xp_gained = Column(Integer, default=0)
    streak_count = Column(Integer, default=1)

    user = relationship("User", back_populates="progress_records")

class Achievement(Base):
    __tablename__ = "achievements"

    achievement_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    achievement_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    earned_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")

class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    exercise_type = Column(String(100), nullable=False)
    reason = Column(Text, nullable=True)
    difficulty = Column(String(50), default="Medium")
    completed = Column(Integer, default=0)  # 0: false, 1: true
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")

class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    model_version = Column(String(50), default="v1.0.0")
    prediction_type = Column(String(50), nullable=False)  # score_prediction, level_classification, weak_area
    prediction = Column(JSON, nullable=False)
    confidence = Column(Float, default=0.95)
    date = Column(DateTime, default=datetime.utcnow)
