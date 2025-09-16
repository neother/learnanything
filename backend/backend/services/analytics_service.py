from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import statistics

from models.analytics import (
    LearningSession, WordProgress, LearningAnalytics, VideoAnalytics,
    AnalyticsSummary, LearningInsights, LearningSessionResponse, WordProgressResponse
)
from models.user import User

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def track_learning_session(
        self,
        user_id: int,
        video_url: str,
        session_number: int,
        total_sessions: int,
        focus_words: List[Dict[str, Any]] = None,
        video_title: str = None
    ) -> LearningSession:
        """Start tracking a new learning session"""
        session = LearningSession(
            user_id=user_id,
            video_url=video_url,
            video_title=video_title,
            session_number=session_number,
            total_sessions=total_sessions,
            focus_words=focus_words,
            status="active"
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def complete_learning_session(
        self,
        session_id: int,
        words_mastered: List[str] = None,
        completion_percentage: float = 1.0
    ) -> Optional[LearningSession]:
        """Mark a learning session as completed"""
        session = self.db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            return None

        now = datetime.utcnow()
        session.completed_at = now
        session.words_mastered = words_mastered or []
        session.completion_percentage = completion_percentage
        session.status = "completed"

        # Calculate session duration
        if session.started_at:
            duration = (now - session.started_at).total_seconds() / 60  # minutes
            session.session_duration = int(duration)

        self.db.commit()
        self.db.refresh(session)

        # Update video analytics
        self._update_video_analytics(session.video_url)

        return session

    def track_word_progress(
        self,
        user_id: int,
        word: str,
        cefr_level: str,
        definition: str = None,
        translation: str = None,
        sentence: str = None,
        video_url: str = None,
        timestamp: float = None,
        session_id: int = None
    ) -> WordProgress:
        """Track progress for a specific word"""

        # Check if word already exists for this user
        existing = self.db.query(WordProgress).filter(
            and_(WordProgress.user_id == user_id, WordProgress.word == word)
        ).first()

        if existing:
            # Update existing word progress
            existing.encounters += 1
            existing.last_reviewed = datetime.utcnow()
            if session_id:
                existing.session_id = session_id
            if sentence:
                existing.sentence = sentence

            word_progress = existing
        else:
            # Create new word progress entry
            word_progress = WordProgress(
                user_id=user_id,
                word=word,
                definition=definition,
                translation=translation,
                cefr_level=cefr_level,
                sentence=sentence,
                video_url=video_url,
                timestamp=timestamp,
                session_id=session_id
            )
            self.db.add(word_progress)

        self.db.commit()
        self.db.refresh(word_progress)
        return word_progress

    def mark_word_mastered(self, user_id: int, word: str) -> Optional[WordProgress]:
        """Mark a word as mastered by the user"""
        word_progress = self.db.query(WordProgress).filter(
            and_(WordProgress.user_id == user_id, WordProgress.word == word)
        ).first()

        if word_progress:
            word_progress.is_mastered = True
            word_progress.mastery_level = 1.0
            word_progress.mastered_at = datetime.utcnow()

            # Update spaced repetition parameters
            word_progress.repetitions += 1
            word_progress.next_review_date = datetime.utcnow() + timedelta(days=7)  # Review in a week

            self.db.commit()
            self.db.refresh(word_progress)

        return word_progress

    def get_user_analytics_summary(self, user_id: int) -> AnalyticsSummary:
        """Get comprehensive analytics summary for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Get basic stats
        total_sessions = self.db.query(LearningSession).filter(
            and_(LearningSession.user_id == user_id, LearningSession.status == "completed")
        ).count()

        words_mastered_count = self.db.query(WordProgress).filter(
            and_(WordProgress.user_id == user_id, WordProgress.is_mastered == True)
        ).count()

        total_study_time = self.db.query(func.sum(LearningSession.session_duration)).filter(
            and_(LearningSession.user_id == user_id, LearningSession.status == "completed")
        ).scalar() or 0

        # Calculate mastery rate
        total_words_encountered = self.db.query(WordProgress).filter(
            WordProgress.user_id == user_id
        ).count()

        mastery_rate = words_mastered_count / total_words_encountered if total_words_encountered > 0 else 0.0

        # Calculate average session time
        avg_session_time = total_study_time / total_sessions if total_sessions > 0 else 0.0

        # Get CEFR level distribution
        level_counts = self.db.query(
            WordProgress.cefr_level,
            func.count(WordProgress.id)
        ).filter(
            and_(WordProgress.user_id == user_id, WordProgress.is_mastered == True)
        ).group_by(WordProgress.cefr_level).all()

        level_distribution = {level: count for level, count in level_counts}

        # Get recent activity
        recent_sessions = self.db.query(LearningSession).filter(
            and_(LearningSession.user_id == user_id, LearningSession.status == "completed")
        ).order_by(desc(LearningSession.completed_at)).limit(5).all()

        recent_activity = [LearningSessionResponse.from_orm(session) for session in recent_sessions]

        return AnalyticsSummary(
            total_study_time=total_study_time,
            sessions_completed=total_sessions,
            words_mastered=words_mastered_count,
            current_streak=user.current_streak,
            mastery_rate=mastery_rate,
            average_session_time=avg_session_time,
            level_distribution=level_distribution,
            recent_activity=recent_activity
        )

    def get_learning_insights(self, user_id: int, days: int = 30) -> LearningInsights:
        """Generate learning insights and recommendations"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Weekly progress data
        weekly_data = self._calculate_weekly_progress(user_id, days)

        # Learning patterns
        patterns = self._analyze_learning_patterns(user_id, cutoff_date)

        # Word mastery trends
        mastery_trends = self._calculate_mastery_trends(user_id, cutoff_date)

        # Generate recommendations
        recommendations = self._generate_recommendations(user_id, cutoff_date)

        # Generate achievements
        achievements = self._check_achievements(user_id)

        return LearningInsights(
            weekly_progress=weekly_data,
            learning_patterns=patterns,
            word_mastery_trends=mastery_trends,
            recommendations=recommendations,
            achievements=achievements
        )

    def get_words_for_review(self, user_id: int, limit: int = 10) -> List[WordProgress]:
        """Get words that need review based on spaced repetition"""
        today = datetime.utcnow()

        words_due = self.db.query(WordProgress).filter(
            and_(
                WordProgress.user_id == user_id,
                WordProgress.is_mastered == True,
                WordProgress.next_review_date <= today
            )
        ).order_by(asc(WordProgress.next_review_date)).limit(limit).all()

        return words_due

    def _calculate_weekly_progress(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """Calculate weekly learning progress"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        sessions = self.db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.completed_at >= cutoff_date,
                LearningSession.status == "completed"
            )
        ).order_by(LearningSession.completed_at).all()

        # Group by week
        weekly_data = defaultdict(lambda: {'sessions': 0, 'study_time': 0, 'words_mastered': 0})

        for session in sessions:
            if session.completed_at:
                week_start = session.completed_at - timedelta(days=session.completed_at.weekday())
                week_key = week_start.strftime('%Y-%m-%d')

                weekly_data[week_key]['sessions'] += 1
                weekly_data[week_key]['study_time'] += session.session_duration or 0
                weekly_data[week_key]['words_mastered'] += len(session.words_mastered or [])

        return [
            {'week': week, **data}
            for week, data in sorted(weekly_data.items())
        ]

    def _analyze_learning_patterns(self, user_id: int, cutoff_date: datetime) -> Dict[str, Any]:
        """Analyze user learning patterns"""
        sessions = self.db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.completed_at >= cutoff_date,
                LearningSession.status == "completed"
            )
        ).all()

        if not sessions:
            return {"message": "Insufficient data for pattern analysis"}

        # Analyze peak learning hours
        hours = [session.started_at.hour for session in sessions if session.started_at]
        hour_counts = Counter(hours)
        peak_hours = hour_counts.most_common(3)

        # Analyze session durations
        durations = [session.session_duration for session in sessions if session.session_duration]
        avg_duration = statistics.mean(durations) if durations else 0

        # Analyze consistency
        dates = [session.completed_at.date() for session in sessions if session.completed_at]
        unique_dates = len(set(dates))
        consistency_score = unique_dates / len(dates) if dates else 0

        return {
            "peak_learning_hours": [{"hour": hour, "sessions": count} for hour, count in peak_hours],
            "average_session_duration": round(avg_duration, 1),
            "consistency_score": round(consistency_score, 2),
            "total_active_days": unique_dates
        }

    def _calculate_mastery_trends(self, user_id: int, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Calculate word mastery trends over time"""
        mastered_words = self.db.query(WordProgress).filter(
            and_(
                WordProgress.user_id == user_id,
                WordProgress.is_mastered == True,
                WordProgress.mastered_at >= cutoff_date
            )
        ).order_by(WordProgress.mastered_at).all()

        # Group by day
        daily_mastery = defaultdict(lambda: defaultdict(int))

        for word in mastered_words:
            if word.mastered_at:
                date_key = word.mastered_at.date().isoformat()
                daily_mastery[date_key][word.cefr_level] += 1

        return [
            {
                "date": date,
                "levels": dict(levels),
                "total": sum(levels.values())
            }
            for date, levels in sorted(daily_mastery.items())
        ]

    def _generate_recommendations(self, user_id: int, cutoff_date: datetime) -> List[Dict[str, str]]:
        """Generate personalized learning recommendations"""
        recommendations = []

        # Check recent activity
        recent_sessions = self.db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.completed_at >= cutoff_date
            )
        ).count()

        if recent_sessions == 0:
            recommendations.append({
                "type": "engagement",
                "title": "Start Learning",
                "message": "Begin your learning journey by selecting a video!"
            })
        elif recent_sessions < 7:
            recommendations.append({
                "type": "consistency",
                "title": "Build Consistency",
                "message": "Try to practice daily for better retention and progress."
            })

        # Check for words due for review
        words_due = self.get_words_for_review(user_id, limit=1)
        if words_due:
            recommendations.append({
                "type": "review",
                "title": "Review Time",
                "message": f"You have {len(words_due)} words ready for review to strengthen your memory."
            })

        # Check mastery rate
        summary = self.get_user_analytics_summary(user_id)
        if summary.mastery_rate < 0.7:
            recommendations.append({
                "type": "difficulty",
                "title": "Focus on Fundamentals",
                "message": "Consider reviewing easier content to build a stronger foundation."
            })

        return recommendations

    def _check_achievements(self, user_id: int) -> List[Dict[str, str]]:
        """Check for user achievements"""
        achievements = []

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return achievements

        # Streak achievements
        if user.current_streak >= 7:
            achievements.append({
                "type": "streak",
                "title": "Week Warrior",
                "description": f"Maintained a {user.current_streak}-day learning streak!"
            })

        if user.current_streak >= 30:
            achievements.append({
                "type": "streak",
                "title": "Monthly Master",
                "description": "Incredible 30-day learning streak!"
            })

        # Word count achievements
        mastered_count = self.db.query(WordProgress).filter(
            and_(WordProgress.user_id == user_id, WordProgress.is_mastered == True)
        ).count()

        if mastered_count >= 100:
            achievements.append({
                "type": "milestone",
                "title": "Century Club",
                "description": "Mastered over 100 words!"
            })

        if mastered_count >= 500:
            achievements.append({
                "type": "milestone",
                "title": "Vocabulary Virtuoso",
                "description": "Amazing! 500+ words mastered!"
            })

        return achievements

    def _update_video_analytics(self, video_url: str):
        """Update analytics for a specific video"""
        video_analytics = self.db.query(VideoAnalytics).filter(
            VideoAnalytics.video_url == video_url
        ).first()

        if not video_analytics:
            video_analytics = VideoAnalytics(video_url=video_url)
            self.db.add(video_analytics)

        # Update usage statistics
        video_analytics.total_sessions += 1
        video_analytics.last_analyzed = datetime.utcnow()

        # Calculate completion rate
        total_sessions = self.db.query(LearningSession).filter(
            LearningSession.video_url == video_url
        ).count()

        completed_sessions = self.db.query(LearningSession).filter(
            and_(
                LearningSession.video_url == video_url,
                LearningSession.status == "completed"
            )
        ).count()

        if total_sessions > 0:
            video_analytics.completion_rate = completed_sessions / total_sessions

        self.db.commit()