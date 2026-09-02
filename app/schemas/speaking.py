from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class SpeakingAnalyzeRequest(BaseModel):
    transcript: str
    duration: float  # in seconds
    topic: Optional[str] = "General Practice"

class SpeakingAnalyzeResponse(BaseModel):
    session_id: Optional[int] = None
    transcript: str
    wpm: float
    filler_count: int
    filler_words: List[str]
    pause_count: int
    average_pause_duration: float
    fluency_score: float
    grammar_score: float
    vocabulary_score: float
    clarity_score: float
    confidence_score: float
    overall_score: float
    feedback: str
    weak_area: str
    recommended_exercise: str

class SpeakingSessionOut(BaseModel):
    session_id: int
    date: datetime
    topic: str
    duration: int
    wpm: float
    filler_count: int
    overall_score: float
    weak_area: Optional[str] = None

    class Config:
        from_attributes = True
