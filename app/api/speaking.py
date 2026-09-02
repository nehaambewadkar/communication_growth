from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.session import SpeakingSession
from app.models.analytics import Progress, MLPrediction
from app.schemas.speaking import SpeakingAnalyzeRequest, SpeakingAnalyzeResponse, SpeakingSessionOut
from app.api.deps import get_current_user
from app.ml.nlp_analyzer import nlp_analyzer
from app.ml.score_predictor import ml_model
from app.ml.adaptive_engine import adaptive_engine

router = APIRouter(prefix="/speaking", tags=["Speaking Analysis"])

@router.post("/analyze", response_model=SpeakingAnalyzeResponse)
def analyze_speech(
    req: SpeakingAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript content cannot be empty.")

    # 1. Speech & NLP Feature Extraction
    nlp_results = nlp_analyzer.analyze(req.transcript, req.duration)

    # 2. Machine Learning Predictions
    ml_results = ml_model.predict(nlp_results)

    # 3. Adaptive Recommendation
    recommendation = adaptive_engine.get_recommendation(ml_results["weak_area"], ml_results["predicted_level"])

    # Construct actionable AI Feedback
    feedback = (
        f"Your speaking rate was {nlp_results['wpm']} WPM with {nlp_results['filler_count']} filler words detected. "
        f"Primary strength identified in {ml_results['strong_area']}. Focus on improving {ml_results['weak_area']} "
        f"to elevate your level from {ml_results['predicted_level']}."
    )

    # 4. Save Session record to Database
    session_rec = SpeakingSession(
        user_id=current_user.user_id,
        topic=req.topic,
        duration=int(req.duration),
        transcript=req.transcript,
        wpm=nlp_results["wpm"],
        filler_count=nlp_results["filler_count"],
        filler_words=nlp_results["filler_words"],
        pause_count=nlp_results["pause_count"],
        average_pause_duration=nlp_results["average_pause_duration"],
        fluency_score=nlp_results["fluency_score"],
        grammar_score=nlp_results["grammar_score"],
        vocabulary_score=nlp_results["vocabulary_score"],
        clarity_score=nlp_results["clarity_score"],
        confidence_score=nlp_results["confidence_score"],
        overall_score=ml_results["predicted_score"],
        feedback=feedback,
        weak_area=ml_results["weak_area"]
    )
    db.add(session_rec)

    # 5. Log ML Prediction history
    pred_rec = MLPrediction(
        user_id=current_user.user_id,
        model_version=ml_results["model_version"],
        prediction_type="score_prediction",
        prediction={"score": ml_results["predicted_score"], "level": ml_results["predicted_level"]},
        confidence=ml_results["confidence"]
    )
    db.add(pred_rec)

    # 6. Save Progress record
    progress_rec = Progress(
        user_id=current_user.user_id,
        component_scores={
            "fluency": nlp_results["fluency_score"],
            "grammar": nlp_results["grammar_score"],
            "vocabulary": nlp_results["vocabulary_score"],
            "clarity": nlp_results["clarity_score"],
            "confidence": nlp_results["confidence_score"]
        },
        overall_score=ml_results["predicted_score"],
        xp_gained=50,
        streak_count=1
    )
    db.add(progress_rec)

    db.commit()
    db.refresh(session_rec)

    return {
        "session_id": session_rec.session_id,
        "transcript": req.transcript,
        "wpm": nlp_results["wpm"],
        "filler_count": nlp_results["filler_count"],
        "filler_words": nlp_results["filler_words"],
        "pause_count": nlp_results["pause_count"],
        "average_pause_duration": nlp_results["average_pause_duration"],
        "fluency_score": nlp_results["fluency_score"],
        "grammar_score": nlp_results["grammar_score"],
        "vocabulary_score": nlp_results["vocabulary_score"],
        "clarity_score": nlp_results["clarity_score"],
        "confidence_score": nlp_results["confidence_score"],
        "overall_score": ml_results["predicted_score"],
        "feedback": feedback,
        "weak_area": ml_results["weak_area"],
        "recommended_exercise": recommendation["title"]
    }

@router.get("/history", response_model=List[SpeakingSessionOut])
def get_speaking_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = (
        db.query(SpeakingSession)
        .filter(SpeakingSession.user_id == current_user.user_id)
        .order_by(SpeakingSession.date.desc())
        .limit(20)
        .all()
    )
    return sessions
