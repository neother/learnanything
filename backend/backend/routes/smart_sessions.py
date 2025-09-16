from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from database import get_db
from auth import get_current_active_user
from models.user import User
from services.smart_session_service import SmartSessionService

router = APIRouter(prefix="/api/smart-sessions", tags=["Smart Session Generation"])

class PersonalizedSessionRequest(BaseModel):
    available_words: List[Dict[str, Any]]
    target_session_size: int = 5
    difficulty_preference: Optional[str] = None  # "easier", "harder", None

class AdaptiveSessionsRequest(BaseModel):
    available_words: List[Dict[str, Any]]
    total_sessions: int = 5
    words_per_session: int = 5

class SessionOptimizationRequest(BaseModel):
    current_session: Dict[str, Any]
    performance_data: Dict[str, Any]

@router.post("/personalized")
async def generate_personalized_session(
    request: PersonalizedSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a single personalized learning session based on user analytics"""
    try:
        smart_session_service = SmartSessionService(db)

        session = smart_session_service.generate_personalized_session(
            user_id=current_user.id,
            available_words=request.available_words,
            target_session_size=request.target_session_size,
            difficulty_preference=request.difficulty_preference
        )

        return {
            "success": True,
            "session": session,
            "user_level": current_user.estimated_level,
            "personalization_applied": True,
            "generated_at": "2025-09-16T05:35:00Z"  # Current timestamp
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session generation error: {str(e)}")

@router.post("/adaptive-series")
async def generate_adaptive_sessions(
    request: AdaptiveSessionsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate multiple adaptive sessions with progressive difficulty"""
    try:
        smart_session_service = SmartSessionService(db)

        sessions = smart_session_service.generate_adaptive_sessions(
            user_id=current_user.id,
            available_words=request.available_words,
            total_sessions=request.total_sessions,
            words_per_session=request.words_per_session
        )

        # Calculate series statistics
        total_words = sum(len(session['focus_words']) for session in sessions)
        difficulty_progression = [session.get('target_difficulty', 0.5) for session in sessions]

        return {
            "success": True,
            "sessions": sessions,
            "series_statistics": {
                "total_sessions": len(sessions),
                "total_words": total_words,
                "difficulty_progression": difficulty_progression,
                "estimated_total_duration": sum(session.get('estimated_duration', 15) for session in sessions)
            },
            "personalization_applied": True,
            "generated_at": "2025-09-16T05:35:00Z"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptive sessions error: {str(e)}")

@router.get("/spaced-repetition")
async def generate_spaced_repetition_session(
    review_type: str = Query("mixed", description="Type of review session"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a spaced repetition review session"""
    try:
        if review_type not in ["due", "overdue", "mixed"]:
            raise HTTPException(status_code=400, detail="Invalid review_type. Must be 'due', 'overdue', or 'mixed'")

        smart_session_service = SmartSessionService(db)

        session = smart_session_service.generate_spaced_repetition_session(
            user_id=current_user.id,
            review_type=review_type
        )

        return {
            "success": True,
            "session": session,
            "review_type": review_type,
            "generated_at": "2025-09-16T05:35:00Z"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spaced repetition error: {str(e)}")

@router.post("/optimize")
async def optimize_session_difficulty(
    request: SessionOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Dynamically optimize session difficulty based on real-time performance"""
    try:
        smart_session_service = SmartSessionService(db)

        optimized_session = smart_session_service.optimize_session_difficulty(
            user_id=current_user.id,
            current_session=request.current_session,
            performance_data=request.performance_data
        )

        return {
            "success": True,
            "optimized_session": optimized_session,
            "optimization_applied": optimized_session.get('difficulty_adjusted', False),
            "performance_score": request.performance_data.get('performance_score'),
            "optimized_at": "2025-09-16T05:35:00Z"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session optimization error: {str(e)}")

@router.get("/recommendations")
async def get_learning_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized learning recommendations"""
    try:
        smart_session_service = SmartSessionService(db)

        # Get user learning profile
        user_profile = smart_session_service._get_user_learning_profile(current_user.id)

        # Generate recommendations based on profile
        recommendations = []

        if user_profile['completion_rate'] < 0.6:
            recommendations.append({
                "type": "difficulty",
                "priority": "high",
                "title": "Consider Easier Content",
                "description": "Your completion rate is below 60%. Try focusing on easier vocabulary to build confidence.",
                "action": "Select videos with more A1-A2 level words"
            })

        if user_profile['learning_consistency'] < 0.3:
            recommendations.append({
                "type": "consistency",
                "priority": "high",
                "title": "Build Learning Habit",
                "description": "Consistent daily practice will improve retention and progress.",
                "action": "Aim for 15-20 minute sessions daily"
            })

        if user_profile['words_per_session'] < 2:
            recommendations.append({
                "type": "efficiency",
                "priority": "medium",
                "title": "Increase Learning Pace",
                "description": "You're learning fewer than 2 words per session on average.",
                "action": "Try focusing on one word at a time during video sessions"
            })

        # Spaced repetition recommendations
        words_for_review = smart_session_service.analytics_service.get_words_for_review(current_user.id, limit=1)
        if words_for_review:
            recommendations.append({
                "type": "review",
                "priority": "medium",
                "title": "Review Time",
                "description": f"You have {len(words_for_review)} words ready for review.",
                "action": "Start a spaced repetition session"
            })

        # Level progression recommendations
        level_proficiency = user_profile.get('level_proficiency', {})
        current_level = current_user.estimated_level
        if level_proficiency.get(current_level, 0.0) > 0.8:
            recommendations.append({
                "type": "progression",
                "priority": "low",
                "title": "Ready for Next Level",
                "description": f"You've mastered over 80% of {current_level} vocabulary.",
                "action": f"Consider advancing to {SmartSessionService._get_next_level(current_level)} content"
            })

        return {
            "success": True,
            "recommendations": recommendations,
            "user_profile_summary": {
                "level": current_user.estimated_level,
                "completion_rate": user_profile['completion_rate'],
                "consistency_score": user_profile['learning_consistency'],
                "words_per_session": user_profile['words_per_session']
            },
            "generated_at": "2025-09-16T05:35:00Z"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations error: {str(e)}")

@router.get("/user-analytics")
async def get_user_learning_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed user learning analytics for session generation"""
    try:
        smart_session_service = SmartSessionService(db)
        user_profile = smart_session_service._get_user_learning_profile(current_user.id)

        return {
            "success": True,
            "analytics": user_profile,
            "insights": {
                "learning_efficiency": "high" if user_profile['words_per_session'] > 3 else "medium" if user_profile['words_per_session'] > 1 else "low",
                "consistency_rating": "excellent" if user_profile['learning_consistency'] > 0.8 else "good" if user_profile['learning_consistency'] > 0.5 else "needs_improvement",
                "difficulty_comfort": "challenging" if user_profile['completion_rate'] < 0.7 else "appropriate" if user_profile['completion_rate'] < 0.9 else "too_easy"
            },
            "next_session_recommendation": {
                "difficulty_preference": "easier" if user_profile['completion_rate'] < 0.6 else "harder" if user_profile['completion_rate'] > 0.9 else None,
                "session_length": "shorter" if user_profile['avg_session_duration'] < 10 else "standard",
                "focus_area": "review" if len(smart_session_service.analytics_service.get_words_for_review(current_user.id, 1)) > 0 else "new_content"
            },
            "generated_at": "2025-09-16T05:35:00Z"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

# Helper method for level progression
@staticmethod
def _get_next_level(current_level: str) -> str:
    """Get the next CEFR level"""
    level_progression = {
        'A1': 'A2',
        'A2': 'B1',
        'B1': 'B2',
        'B2': 'C1',
        'C1': 'C2',
        'C2': 'C2'  # Max level
    }
    return level_progression.get(current_level, 'A2')

# Add the static method to SmartSessionService class
SmartSessionService._get_next_level = _get_next_level