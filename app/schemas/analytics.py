from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class DashboardSummary(BaseModel):
    overall_score: float
    current_level: str
    practice_streak: int
    sessions_completed: int
    words_mastered: int
    weakest_area: str
    strongest_area: str
    recommended_next_activity: str
    component_scores: Dict[str, float]
    recent_trend: List[Dict[str, Any]]
