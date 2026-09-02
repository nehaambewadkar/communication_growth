from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

class WritingAnalyzeRequest(BaseModel):
    text: str

class WritingAnalyzeResponse(BaseModel):
    session_id: Optional[int] = None
    original_text: str
    corrected_text: str
    error_categories: Dict[str, int]
    suggestions: List[str]
    grammar_score: float
    vocabulary_score: float
    overall_score: float
    feedback: str

class WritingSessionOut(BaseModel):
    session_id: int
    date: datetime
    original_text: str
    overall_score: float
    grammar_score: float
    vocabulary_score: float

    class Config:
        from_attributes = True
