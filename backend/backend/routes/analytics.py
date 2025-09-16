from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from auth import get_current_active_user
from models.user import User
from models.analytics import (
    LearningSession, WordProgress, AnalyticsSummary, LearningInsights,
    LearningSessionResponse, WordProgressResponse
)
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Learning Analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics summary for the current user"""
    try:
        analytics_service = AnalyticsService(db)
        summary = analytics_service.get_user_analytics_summary(current_user.id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@router.get("/insights", response_model=LearningInsights)
async def get_learning_insights(
    days: int = Query(30, description="Number of days to analyze", ge=7, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get learning insights and recommendations"""
    try:
        analytics_service = AnalyticsService(db)
        insights = analytics_service.get_learning_insights(current_user.id, days)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights error: {str(e)}")

@router.get("/sessions", response_model=List[LearningSessionResponse])
async def get_learning_sessions(
    limit: int = Query(20, description="Maximum number of sessions to return", ge=1, le=100),
    offset: int = Query(0, description="Number of sessions to skip", ge=0),
    video_url: Optional[str] = Query(None, description="Filter by video URL"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's learning sessions with optional filtering"""
    try:
        query = db.query(LearningSession).filter(LearningSession.user_id == current_user.id)

        if video_url:
            query = query.filter(LearningSession.video_url == video_url)

        sessions = query.order_by(LearningSession.started_at.desc()).offset(offset).limit(limit).all()
        return [LearningSessionResponse.from_orm(session) for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sessions error: {str(e)}")

@router.post("/sessions/start")
async def start_learning_session(
    video_url: str,
    session_number: int,
    total_sessions: int,
    video_title: Optional[str] = None,
    focus_words: Optional[List[dict]] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start tracking a new learning session"""
    try:
        analytics_service = AnalyticsService(db)
        session = analytics_service.track_learning_session(
            user_id=current_user.id,
            video_url=video_url,
            session_number=session_number,
            total_sessions=total_sessions,
            focus_words=focus_words,
            video_title=video_title
        )
        return {
            "session_id": session.id,
            "message": "Learning session started successfully",
            "started_at": session.started_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session start error: {str(e)}")

@router.put("/sessions/{session_id}/complete")
async def complete_learning_session(
    session_id: int,
    words_mastered: Optional[List[str]] = None,
    completion_percentage: float = 1.0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a learning session as completed"""
    try:
        analytics_service = AnalyticsService(db)

        # Verify session belongs to current user
        session = db.query(LearningSession).filter(
            LearningSession.id == session_id,
            LearningSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        completed_session = analytics_service.complete_learning_session(
            session_id=session_id,
            words_mastered=words_mastered or [],
            completion_percentage=completion_percentage
        )

        if not completed_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": completed_session.id,
            "message": "Learning session completed successfully",
            "completed_at": completed_session.completed_at,
            "session_duration": completed_session.session_duration
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session completion error: {str(e)}")

@router.post("/words/track")
async def track_word_progress(
    word: str,
    cefr_level: str,
    definition: Optional[str] = None,
    translation: Optional[str] = None,
    sentence: Optional[str] = None,
    video_url: Optional[str] = None,
    timestamp: Optional[float] = None,
    session_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Track progress for a specific word"""
    try:
        analytics_service = AnalyticsService(db)
        word_progress = analytics_service.track_word_progress(
            user_id=current_user.id,
            word=word,
            cefr_level=cefr_level,
            definition=definition,
            translation=translation,
            sentence=sentence,
            video_url=video_url,
            timestamp=timestamp,
            session_id=session_id
        )

        return {
            "word_progress_id": word_progress.id,
            "word": word_progress.word,
            "encounters": word_progress.encounters,
            "mastery_level": word_progress.mastery_level,
            "message": "Word progress tracked successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word tracking error: {str(e)}")

@router.put("/words/{word}/master")
async def mark_word_mastered(
    word: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a word as mastered by the user"""
    try:
        analytics_service = AnalyticsService(db)
        word_progress = analytics_service.mark_word_mastered(current_user.id, word)

        if not word_progress:
            raise HTTPException(status_code=404, detail="Word not found in user progress")

        return {
            "word": word_progress.word,
            "mastered_at": word_progress.mastered_at,
            "mastery_level": word_progress.mastery_level,
            "next_review_date": word_progress.next_review_date,
            "message": "Word marked as mastered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word mastery error: {str(e)}")

@router.get("/words", response_model=List[WordProgressResponse])
async def get_word_progress(
    limit: int = Query(50, description="Maximum number of words to return", ge=1, le=500),
    offset: int = Query(0, description="Number of words to skip", ge=0),
    cefr_level: Optional[str] = Query(None, description="Filter by CEFR level"),
    mastered_only: bool = Query(False, description="Show only mastered words"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's word progress with optional filtering"""
    try:
        query = db.query(WordProgress).filter(WordProgress.user_id == current_user.id)

        if cefr_level:
            query = query.filter(WordProgress.cefr_level == cefr_level.upper())

        if mastered_only:
            query = query.filter(WordProgress.is_mastered == True)

        words = query.order_by(WordProgress.last_reviewed.desc()).offset(offset).limit(limit).all()
        return [WordProgressResponse.from_orm(word) for word in words]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word progress error: {str(e)}")

@router.get("/words/review", response_model=List[WordProgressResponse])
async def get_words_for_review(
    limit: int = Query(10, description="Maximum number of words to return", ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get words that need review based on spaced repetition"""
    try:
        analytics_service = AnalyticsService(db)
        words_due = analytics_service.get_words_for_review(current_user.id, limit)
        return [WordProgressResponse.from_orm(word) for word in words_due]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review words error: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data for the user"""
    try:
        analytics_service = AnalyticsService(db)

        # Get summary and insights
        summary = analytics_service.get_user_analytics_summary(current_user.id)
        insights = analytics_service.get_learning_insights(current_user.id, days=7)  # Last week
        review_words = analytics_service.get_words_for_review(current_user.id, limit=5)

        # Get recent sessions
        recent_sessions = db.query(LearningSession).filter(
            LearningSession.user_id == current_user.id
        ).order_by(LearningSession.started_at.desc()).limit(3).all()

        return {
            "summary": summary,
            "weekly_insights": insights,
            "words_for_review": [WordProgressResponse.from_orm(word) for word in review_words],
            "recent_sessions": [LearningSessionResponse.from_orm(session) for session in recent_sessions],
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")