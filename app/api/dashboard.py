from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User, Profile
from app.models.session import SpeakingSession, WritingSession
from app.models.vocabulary import VocabularyItem
from app.models.analytics import Progress, Recommendation
from app.schemas.analytics import DashboardSummary
from app.api.deps import get_current_user
from app.ml.adaptive_engine import adaptive_engine

router = APIRouter(tags=["Analytics & Dashboard"])


def _calculate_streak(sessions: list) -> int:
    """
    Calculate practice streak in days from a list of SpeakingSession objects
    ordered by date descending. A streak is consecutive calendar days with at
    least one session recorded (including today or yesterday as the seed).
    """
    if not sessions:
        return 0
    today = datetime.utcnow().date()
    # Collect unique session dates
    session_dates = sorted(
        {s.date.date() for s in sessions if s.date},
        reverse=True
    )
    # Streak must start from today or yesterday to be "active"
    if session_dates[0] < today - timedelta(days=1):
        return 0
    streak = 1
    for i in range(1, len(session_dates)):
        if session_dates[i - 1] - session_dates[i] == timedelta(days=1):
            streak += 1
        else:
            break
    return streak

@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    target_level = profile.target_level if profile else "Intermediate"

    # Fetch speaking sessions
    speaking_sessions = (
        db.query(SpeakingSession)
        .filter(SpeakingSession.user_id == current_user.user_id)
        .order_by(SpeakingSession.date.desc())
        .all()
    )

    total_sessions = len(speaking_sessions)
    
    if total_sessions > 0:
        latest = speaking_sessions[0]
        overall_score = round(latest.overall_score, 1)
        weakest_area = latest.weak_area or "Fluency"
        comp_scores = {
            "Fluency": round(latest.fluency_score, 1),
            "Grammar": round(latest.grammar_score, 1),
            "Vocabulary": round(latest.vocabulary_score, 1),
            "Clarity": round(latest.clarity_score, 1),
            "Confidence": round(latest.confidence_score, 1)
        }
        strongest_area = max(comp_scores, key=comp_scores.get)
    else:
        # No sessions yet — return honest zero/null state, no fake placeholder data
        overall_score = 0.0
        weakest_area = None
        strongest_area = None
        comp_scores = {
            "Fluency": 0.0,
            "Grammar": 0.0,
            "Vocabulary": 0.0,
            "Clarity": 0.0,
            "Confidence": 0.0
        }

    # Trend: only real sessions, no synthetic seed data
    if total_sessions >= 1:
        chronological = list(reversed(speaking_sessions[:10]))
        recent_trend = [
            {
                "session": f"Session {i + 1}",
                "score": round(s.overall_score, 1),
                "wpm": round(s.wpm, 1),
                "fillers": s.filler_count
            }
            for i, s in enumerate(chronological)
        ]
    else:
        recent_trend = []

    # Count vocab items
    mastered_count = db.query(VocabularyItem).filter(
        VocabularyItem.user_id == current_user.user_id,
        VocabularyItem.mastery_level == "Mastered"
    ).count()

    practice_streak = _calculate_streak(speaking_sessions)
    rec = adaptive_engine.get_recommendation(weakest_area or "Fluency", target_level)

    return {
        "overall_score": overall_score,
        "current_level": target_level,
        "practice_streak": practice_streak,
        "sessions_completed": total_sessions,
        "words_mastered": mastered_count,
        "weakest_area": weakest_area,
        "strongest_area": strongest_area,
        "recommended_next_activity": rec["title"] if total_sessions > 0 else None,
        "component_scores": comp_scores,
        "recent_trend": recent_trend
    }

@router.get("/recommendations")
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    user_type = current_user.user_type or "Student"
    
    latest_speaking = (
        db.query(SpeakingSession)
        .filter(SpeakingSession.user_id == current_user.user_id)
        .order_by(SpeakingSession.date.desc())
        .first()
    )
    weak_area = latest_speaking.weak_area if latest_speaking else "Fluency"

    schedule_7_day = adaptive_engine.generate_7_day_plan(weak_area, user_type)
    immediate_recommendation = adaptive_engine.get_recommendation(weak_area)

    return {
        "immediate_task": immediate_recommendation,
        "weekly_plan": schedule_7_day
    }
