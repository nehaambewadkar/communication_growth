from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.session import WritingSession
from app.schemas.writing import WritingAnalyzeRequest, WritingAnalyzeResponse, WritingSessionOut
from app.api.deps import get_current_user
from app.ml.grammar_checker import grammar_coach

router = APIRouter(prefix="/writing", tags=["Writing Coach"])

@router.post("/analyze", response_model=WritingAnalyzeResponse)
def analyze_writing(
    req: WritingAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")

    results = grammar_coach.analyze(req.text)

    # Save writing session
    session_rec = WritingSession(
        user_id=current_user.user_id,
        original_text=results["original_text"],
        corrected_text=results["corrected_text"],
        error_categories=results["error_categories"],
        grammar_score=results["grammar_score"],
        vocabulary_score=results["vocabulary_score"],
        overall_score=results["overall_score"],
        feedback=results["feedback"]
    )
    db.add(session_rec)
    db.commit()
    db.refresh(session_rec)

    return {
        "session_id": session_rec.session_id,
        "original_text": results["original_text"],
        "corrected_text": results["corrected_text"],
        "error_categories": results["error_categories"],
        "suggestions": results["suggestions"],
        "grammar_score": results["grammar_score"],
        "vocabulary_score": results["vocabulary_score"],
        "overall_score": results["overall_score"],
        "feedback": results["feedback"]
    }

@router.get("/history", response_model=List[WritingSessionOut])
def get_writing_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = (
        db.query(WritingSession)
        .filter(WritingSession.user_id == current_user.user_id)
        .order_by(WritingSession.date.desc())
        .limit(20)
        .all()
    )
    return sessions
