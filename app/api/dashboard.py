from typing import Dict, Any, List
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
        overall_score = latest.overall_score
        weakest_area = latest.weak_area or "Fluency"
        comp_scores = {
            "Fluency": latest.fluency_score,
            "Grammar": latest.grammar_score,
            "Vocabulary": latest.vocabulary_score,
            "Clarity": latest.clarity_score,
            "Confidence": latest.confidence_score
        }
        strongest_area = max(comp_scores, key=comp_scores.get)
    else:
        overall_score = profile.baseline_score if profile else 62.0
        weakest_area = "Fluency"
        strongest_area = "Vocabulary"
        comp_scores = {
            "Fluency": 60.0,
            "Grammar": 68.0,
            "Vocabulary": 72.0,
            "Clarity": 65.0,
            "Confidence": 58.0
        }

    # Trend calculation (last 5 sessions or default seed trend)
    if total_sessions >= 2:
        recent_trend = [
            {"session": f"Session {total_sessions - i}", "score": s.overall_score, "wpm": s.wpm, "fillers": s.filler_count}
            for i, s in enumerate(reversed(speaking_sessions[:6]))
        ]
    else:
        recent_trend = [
            {"session": "Baseline", "score": 58.0, "wpm": 115, "fillers": 6},
            {"session": "Practice 1", "score": 63.5, "wpm": 128, "fillers": 4},
            {"session": "Practice 2", "score": 68.0, "wpm": 135, "fillers": 3},
            {"session": "Latest", "score": overall_score, "wpm": 140, "fillers": 2}
        ]

    # Count vocab items
    mastered_count = db.query(VocabularyItem).filter(
        VocabularyItem.user_id == current_user.user_id,
        VocabularyItem.mastery_level == "Mastered"
    ).count()

    rec = adaptive_engine.get_recommendation(weakest_area, target_level)

    return {
        "overall_score": overall_score,
        "current_level": target_level,
        "practice_streak": 3 if total_sessions > 0 else 1,
        "sessions_completed": total_sessions,
        "words_mastered": mastered_count,
        "weakest_area": weakest_area,
        "strongest_area": strongest_area,
        "recommended_next_activity": rec["title"],
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
