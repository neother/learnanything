from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import random
import math
import statistics

from models.user import User
from models.analytics import WordProgress, LearningSession, LearningAnalytics
from services.analytics_service import AnalyticsService

class SmartSessionService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    def generate_personalized_session(
        self,
        user_id: int,
        available_words: List[Dict[str, Any]],
        target_session_size: int = 5,
        difficulty_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a personalized learning session based on user analytics and preferences"""

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Get user's learning analytics
        user_analytics = self._get_user_learning_profile(user_id)

        # Filter and score words
        word_candidates = self._prepare_word_candidates(user_id, available_words, user_analytics)

        # Apply personalized selection algorithm
        selected_words = self._select_optimal_words(
            word_candidates,
            target_session_size,
            user_analytics,
            difficulty_preference
        )

        # Calculate optimal session structure
        session_structure = self._calculate_session_structure(selected_words, user_analytics)

        # Generate learning recommendations
        recommendations = self._generate_session_recommendations(user_analytics, selected_words)

        return {
            "session_words": selected_words,
            "session_structure": session_structure,
            "recommendations": recommendations,
            "estimated_duration": self._estimate_session_duration(selected_words, user_analytics),
            "difficulty_distribution": self._analyze_difficulty_distribution(selected_words),
            "learning_objectives": self._generate_learning_objectives(selected_words, user_analytics)
        }

    def generate_adaptive_sessions(
        self,
        user_id: int,
        available_words: List[Dict[str, Any]],
        total_sessions: int = 5,
        words_per_session: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate multiple adaptive sessions with progressive difficulty"""

        user_analytics = self._get_user_learning_profile(user_id)
        word_candidates = self._prepare_word_candidates(user_id, available_words, user_analytics)

        sessions = []
        used_words = set()

        for session_number in range(1, total_sessions + 1):
            # Calculate adaptive difficulty for this session
            session_difficulty = self._calculate_adaptive_difficulty(
                session_number,
                total_sessions,
                user_analytics
            )

            # Filter available words for this session
            available_for_session = [
                word for word in word_candidates
                if word['word'] not in used_words
            ]

            if len(available_for_session) < words_per_session:
                # If not enough words, fill with review words or easier alternatives
                available_for_session.extend(
                    self._get_review_words(user_id, words_per_session - len(available_for_session))
                )

            # Select words for this specific session
            session_words = self._select_session_words(
                available_for_session,
                words_per_session,
                session_difficulty,
                user_analytics
            )

            # Track used words
            for word in session_words:
                used_words.add(word['word'])

            # Create session structure
            session = {
                "session_id": f"adaptive_session_{session_number}",
                "session_number": session_number,
                "total_sessions": total_sessions,
                "focus_words": session_words,
                "target_difficulty": session_difficulty,
                "session_type": self._determine_session_type(session_number, total_sessions, user_analytics),
                "estimated_duration": self._estimate_session_duration(session_words, user_analytics),
                "learning_objectives": self._generate_session_objectives(session_words, session_number),
                "practice_recommendations": self._generate_practice_recommendations(session_words, user_analytics)
            }

            sessions.append(session)

        return sessions

    def generate_spaced_repetition_session(
        self,
        user_id: int,
        review_type: str = "mixed"  # "due", "overdue", "mixed"
    ) -> Dict[str, Any]:
        """Generate a spaced repetition review session"""

        # Get words due for review
        words_due = self.analytics_service.get_words_for_review(user_id, limit=20)

        if not words_due:
            return {
                "session_type": "no_review_needed",
                "message": "No words currently due for review",
                "next_review_date": self._get_next_review_date(user_id)
            }

        # Categorize review words
        overdue_words = [w for w in words_due if w.next_review_date < datetime.utcnow() - timedelta(days=1)]
        due_today = [w for w in words_due if w.next_review_date <= datetime.utcnow()]

        # Select words based on review type
        if review_type == "overdue" and overdue_words:
            review_words = overdue_words[:10]
        elif review_type == "due" and due_today:
            review_words = due_today[:10]
        else:  # mixed
            review_words = (overdue_words[:5] + due_today[:5])[:10]

        # Convert to session format
        session_words = []
        for word_progress in review_words:
            session_words.append({
                "word": word_progress.word,
                "definition": word_progress.definition,
                "translation": word_progress.translation,
                "level": word_progress.cefr_level,
                "sentence": word_progress.sentence,
                "encounters": word_progress.encounters,
                "mastery_level": word_progress.mastery_level,
                "last_reviewed": word_progress.last_reviewed.isoformat(),
                "review_priority": self._calculate_review_priority(word_progress)
            })

        return {
            "session_type": "spaced_repetition",
            "focus_words": session_words,
            "total_overdue": len(overdue_words),
            "total_due_today": len(due_today),
            "estimated_duration": len(session_words) * 2,  # 2 minutes per word for review
            "review_instructions": self._generate_review_instructions(review_words),
            "success_criteria": self._generate_review_success_criteria(len(session_words))
        }

    def optimize_session_difficulty(
        self,
        user_id: int,
        current_session: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dynamically optimize session difficulty based on real-time performance"""

        user_analytics = self._get_user_learning_profile(user_id)

        # Analyze current performance
        mastery_rate = performance_data.get('mastery_rate', 0.0)
        average_attempts = performance_data.get('average_attempts', 1.0)
        session_duration = performance_data.get('session_duration', 0)

        # Calculate performance score (0.0 to 1.0)
        performance_score = self._calculate_performance_score(mastery_rate, average_attempts, session_duration)

        # Determine if adjustment is needed
        adjustment_needed = False
        adjustment_direction = 0  # -1 = easier, 0 = no change, 1 = harder

        if performance_score < 0.3:  # Struggling
            adjustment_needed = True
            adjustment_direction = -1
        elif performance_score > 0.8:  # Too easy
            adjustment_needed = True
            adjustment_direction = 1

        optimized_session = current_session.copy()

        if adjustment_needed:
            # Adjust word selection
            optimized_session['focus_words'] = self._adjust_word_difficulty(
                current_session['focus_words'],
                adjustment_direction,
                user_analytics
            )

            # Update session metadata
            optimized_session['difficulty_adjusted'] = True
            optimized_session['adjustment_direction'] = adjustment_direction
            optimized_session['performance_trigger'] = performance_score
            optimized_session['optimization_reason'] = self._get_optimization_reason(adjustment_direction)

        return optimized_session

    def _get_user_learning_profile(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user learning profile"""
        user = self.db.query(User).filter(User.id == user_id).first()

        # Get recent performance metrics
        recent_sessions = self.db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.completed_at >= datetime.utcnow() - timedelta(days=30),
                LearningSession.status == "completed"
            )
        ).all()

        # Get word progress statistics
        word_stats = self.db.query(
            WordProgress.cefr_level,
            func.count(WordProgress.id).label('total'),
            func.sum(func.cast(WordProgress.is_mastered, float)).label('mastered')
        ).filter(WordProgress.user_id == user_id).group_by(WordProgress.cefr_level).all()

        # Calculate performance metrics
        if recent_sessions:
            avg_session_duration = statistics.mean([s.session_duration or 0 for s in recent_sessions])
            completion_rate = len([s for s in recent_sessions if s.completion_percentage >= 0.8]) / len(recent_sessions)

            all_mastered_words = []
            for session in recent_sessions:
                if session.words_mastered:
                    all_mastered_words.extend(session.words_mastered)

            words_per_session = len(all_mastered_words) / len(recent_sessions) if recent_sessions else 0
        else:
            avg_session_duration = 15  # Default
            completion_rate = 0.7  # Default
            words_per_session = 3  # Default

        # Build level proficiency map
        level_proficiency = {}
        for level, total, mastered in word_stats:
            level_proficiency[level] = (mastered or 0) / (total or 1)

        return {
            "user_level": user.estimated_level,
            "current_streak": user.current_streak,
            "total_study_time": user.total_study_time,
            "words_learned": user.words_learned,
            "avg_session_duration": avg_session_duration,
            "completion_rate": completion_rate,
            "words_per_session": words_per_session,
            "level_proficiency": level_proficiency,
            "learning_consistency": min(user.current_streak / 7.0, 1.0),  # Normalize to 0-1
            "recent_sessions_count": len(recent_sessions)
        }

    def _prepare_word_candidates(
        self,
        user_id: int,
        available_words: List[Dict[str, Any]],
        user_analytics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prepare and score word candidates for selection"""

        # Get user's word progress
        known_words = self.db.query(WordProgress).filter(WordProgress.user_id == user_id).all()
        known_word_set = {wp.word for wp in known_words}
        mastered_word_set = {wp.word for wp in known_words if wp.is_mastered}

        candidates = []

        for word_data in available_words:
            word = word_data['word']
            level = word_data.get('level', 'A2')

            # Skip already mastered words
            if word in mastered_word_set:
                continue

            # Calculate word difficulty score
            difficulty_score = self._calculate_word_difficulty(word_data, user_analytics)

            # Calculate learning priority
            priority_score = self._calculate_learning_priority(word, level, user_analytics, word in known_word_set)

            # Calculate optimal timing score
            timing_score = self._calculate_timing_score(word_data, user_analytics)

            # Combine scores
            total_score = (difficulty_score * 0.3) + (priority_score * 0.5) + (timing_score * 0.2)

            candidates.append({
                **word_data,
                'difficulty_score': difficulty_score,
                'priority_score': priority_score,
                'timing_score': timing_score,
                'total_score': total_score,
                'is_known': word in known_word_set
            })

        # Sort by total score
        return sorted(candidates, key=lambda x: x['total_score'], reverse=True)

    def _select_optimal_words(
        self,
        candidates: List[Dict[str, Any]],
        target_size: int,
        user_analytics: Dict[str, Any],
        difficulty_preference: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Select optimal words using advanced selection algorithm"""

        if len(candidates) <= target_size:
            return candidates

        selected = []
        used_levels = Counter()

        # Apply difficulty preference
        if difficulty_preference == "easier":
            candidates = [c for c in candidates if self._get_level_numeric(c.get('level', 'A2')) <= 3]
        elif difficulty_preference == "harder":
            candidates = [c for c in candidates if self._get_level_numeric(c.get('level', 'A2')) >= 3]

        # Diversified selection algorithm
        for i in range(target_size):
            if i < len(candidates):
                # For the first few selections, use highest scores
                if i < target_size // 2:
                    selected.append(candidates[i])
                else:
                    # For later selections, ensure level diversity
                    remaining_candidates = candidates[len(selected):]

                    # Prefer levels that are underrepresented
                    min_level_count = min(used_levels.values()) if used_levels else 0
                    diverse_candidates = [
                        c for c in remaining_candidates
                        if used_levels.get(c.get('level', 'A2'), 0) <= min_level_count
                    ]

                    if diverse_candidates:
                        selected.append(diverse_candidates[0])
                    else:
                        selected.append(remaining_candidates[0])

                # Track level usage
                level = selected[-1].get('level', 'A2')
                used_levels[level] += 1

        return selected

    def _calculate_adaptive_difficulty(
        self,
        session_number: int,
        total_sessions: int,
        user_analytics: Dict[str, Any]
    ) -> float:
        """Calculate adaptive difficulty for a specific session"""

        base_difficulty = 0.5  # Base difficulty (0.0 = very easy, 1.0 = very hard)

        # Progressive difficulty increase
        progression_factor = (session_number - 1) / (total_sessions - 1) if total_sessions > 1 else 0

        # User performance adjustment
        performance_multiplier = 1.0
        if user_analytics['completion_rate'] > 0.9:
            performance_multiplier = 1.2  # Make it harder
        elif user_analytics['completion_rate'] < 0.6:
            performance_multiplier = 0.8  # Make it easier

        # Consistency bonus
        consistency_bonus = user_analytics['learning_consistency'] * 0.1

        final_difficulty = min(1.0, (base_difficulty + progression_factor * 0.3) * performance_multiplier + consistency_bonus)

        return final_difficulty

    def _calculate_word_difficulty(self, word_data: Dict[str, Any], user_analytics: Dict[str, Any]) -> float:
        """Calculate difficulty score for a word"""
        level = word_data.get('level', 'A2')
        level_numeric = self._get_level_numeric(level)
        user_level_numeric = self._get_level_numeric(user_analytics['user_level'])

        # Difficulty based on level difference
        level_difference = level_numeric - user_level_numeric

        if level_difference <= -2:
            return 0.2  # Very easy
        elif level_difference == -1:
            return 0.4  # Easy
        elif level_difference == 0:
            return 0.6  # Appropriate
        elif level_difference == 1:
            return 0.8  # Challenging
        else:
            return 1.0  # Very challenging

    def _calculate_learning_priority(
        self,
        word: str,
        level: str,
        user_analytics: Dict[str, Any],
        is_known: bool
    ) -> float:
        """Calculate learning priority for a word"""
        priority = 0.5  # Base priority

        # Boost priority for words at user's level
        user_level_numeric = self._get_level_numeric(user_analytics['user_level'])
        word_level_numeric = self._get_level_numeric(level)

        if word_level_numeric == user_level_numeric:
            priority += 0.3
        elif abs(word_level_numeric - user_level_numeric) == 1:
            priority += 0.2

        # Boost for words at levels with low proficiency
        level_proficiency = user_analytics['level_proficiency'].get(level, 0.0)
        if level_proficiency < 0.5:
            priority += 0.2

        # Penalty for already known words (but not completely eliminate them)
        if is_known:
            priority *= 0.7

        return min(1.0, priority)

    def _calculate_timing_score(self, word_data: Dict[str, Any], user_analytics: Dict[str, Any]) -> float:
        """Calculate optimal timing score for introducing a word"""
        # Higher scores for words that appear earlier in the video
        timestamp = word_data.get('timestamp', 0)
        if timestamp < 300:  # First 5 minutes
            return 0.8
        elif timestamp < 900:  # First 15 minutes
            return 0.6
        else:
            return 0.4

    def _get_level_numeric(self, level: str) -> int:
        """Convert CEFR level to numeric value"""
        level_map = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        return level_map.get(level.upper(), 2)

    def _calculate_session_structure(self, selected_words: List[Dict[str, Any]], user_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal session structure"""
        total_words = len(selected_words)

        # Determine session phases
        preview_phase = max(1, total_words // 3)
        practice_phase = total_words - preview_phase

        return {
            "total_words": total_words,
            "preview_phase": {
                "word_count": preview_phase,
                "estimated_duration": preview_phase * 1.5,  # minutes per word
                "focus": "introduction_and_context"
            },
            "practice_phase": {
                "word_count": practice_phase,
                "estimated_duration": practice_phase * 2.5,  # minutes per word
                "focus": "active_learning_and_mastery"
            },
            "recommended_breaks": max(1, total_words // 4)
        }

    def _estimate_session_duration(self, selected_words: List[Dict[str, Any]], user_analytics: Dict[str, Any]) -> int:
        """Estimate session duration in minutes"""
        base_time_per_word = 3.0  # minutes

        # Adjust based on user's average session performance
        user_multiplier = user_analytics['avg_session_duration'] / (user_analytics['words_per_session'] * base_time_per_word)
        user_multiplier = max(0.5, min(2.0, user_multiplier))  # Clamp between 0.5x and 2x

        estimated_minutes = len(selected_words) * base_time_per_word * user_multiplier
        return int(estimated_minutes)

    def _analyze_difficulty_distribution(self, selected_words: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze CEFR difficulty distribution of selected words"""
        distribution = Counter(word.get('level', 'A2') for word in selected_words)
        return dict(distribution)

    def _generate_learning_objectives(self, selected_words: List[Dict[str, Any]], user_analytics: Dict[str, Any]) -> List[str]:
        """Generate specific learning objectives for the session"""
        objectives = []

        level_distribution = self._analyze_difficulty_distribution(selected_words)

        for level, count in level_distribution.items():
            if count == 1:
                objectives.append(f"Learn 1 new {level}-level word")
            else:
                objectives.append(f"Learn {count} new {level}-level words")

        # Add performance-based objectives
        if user_analytics['completion_rate'] < 0.8:
            objectives.append("Focus on understanding and retention")
        else:
            objectives.append("Challenge yourself with advanced usage")

        return objectives

    def _get_next_review_date(self, user_id: int) -> Optional[str]:
        """Get the next review date for the user"""
        next_review = self.db.query(WordProgress.next_review_date).filter(
            and_(
                WordProgress.user_id == user_id,
                WordProgress.next_review_date > datetime.utcnow()
            )
        ).order_by(WordProgress.next_review_date).first()

        return next_review[0].isoformat() if next_review else None

    def _calculate_review_priority(self, word_progress: WordProgress) -> float:
        """Calculate review priority for a word"""
        days_overdue = (datetime.utcnow() - word_progress.next_review_date).days if word_progress.next_review_date else 0
        mastery_level = word_progress.mastery_level

        # Higher priority for overdue words with lower mastery
        priority = (days_overdue * 0.1) + (1.0 - mastery_level)
        return min(1.0, priority)

    def _calculate_performance_score(self, mastery_rate: float, average_attempts: float, session_duration: int) -> float:
        """Calculate overall performance score"""
        # Normalize components
        mastery_component = mastery_rate  # 0.0 to 1.0
        efficiency_component = max(0.0, 1.0 - (average_attempts - 1.0) / 3.0)  # Fewer attempts = better
        speed_component = max(0.0, 1.0 - (session_duration - 10) / 20.0)  # Optimal around 10-15 minutes

        return (mastery_component * 0.5) + (efficiency_component * 0.3) + (speed_component * 0.2)

    # Additional helper methods would continue here...
    def _generate_session_recommendations(self, user_analytics: Dict[str, Any], selected_words: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for the session"""
        recommendations = []

        if user_analytics['learning_consistency'] < 0.5:
            recommendations.append("Try to maintain daily practice for better retention")

        if len([w for w in selected_words if w.get('level') in ['C1', 'C2']]) > len(selected_words) // 2:
            recommendations.append("This session contains advanced vocabulary - take your time")

        return recommendations