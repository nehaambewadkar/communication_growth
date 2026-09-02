from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class VocabularyItem(Base):
    __tablename__ = "vocabulary"

    word_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    word = Column(String(100), nullable=False, index=True)
    meaning = Column(Text, nullable=True)
    example_sentence = Column(Text, nullable=True)
    mastery_level = Column(String(50), default="Learning")  # Learning, Practiced, Mastered
    date_learned = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=1)

    user = relationship("User", back_populates="vocabulary_items")
