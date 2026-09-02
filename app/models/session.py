from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class SpeakingSession(Base):
    __tablename__ = "speaking_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    topic = Column(String(200), default="General Speaking")
    duration = Column(Integer, default=0)  # seconds
    transcript = Column(Text, nullable=True)
    
    # NLP & Speech metrics
    wpm = Column(Float, default=0.0)
    filler_count = Column(Integer, default=0)
    filler_words = Column(JSON, default=list)  # list of filler occurrences
    pause_count = Column(Integer, default=0)
    average_pause_duration = Column(Float, default=0.0)
    
    # Sub-scores (0-100)
    fluency_score = Column(Float, default=0.0)
    grammar_score = Column(Float, default=0.0)
    vocabulary_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    feedback = Column(Text, nullable=True)
    weak_area = Column(String(50), nullable=True)

    user = relationship("User", back_populates="speaking_sessions")

class WritingSession(Base):
    __tablename__ = "writing_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=True)
    error_categories = Column(JSON, default=dict)  # e.g., {"tenses": 2, "prepositions": 1}
    grammar_score = Column(Float, default=0.0)
    vocabulary_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)

    user = relationship("User", back_populates="writing_sessions")

class ListeningSession(Base):
    __tablename__ = "listening_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    exercise_id = Column(String(100), nullable=False)
    comprehension_score = Column(Float, default=0.0)
    answers = Column(JSON, default=dict)

    user = relationship("User", back_populates="listening_sessions")
