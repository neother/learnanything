from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from .user import Base

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Video Information
    video_url = Column(String, nullable=False)
    video_title = Column(String, nullable=True)
    video_duration = Column(Integer, nullable=True)  # in seconds

    # Session Details
    session_number = Column(Integer, nullable=False)  # 1, 2, 3...
    total_sessions = Column(Integer, nullable=False)
    focus_words = Column(JSON, nullable=True)  # List of words in this session

    # Progress Metrics
    words_encountered = Column(JSON, nullable=True)  # Words actually encountered
    words_mastered = Column(JSON, nullable=True)     # Words marked as mastered
    session_duration = Column(Integer, nullable=True)  # in minutes
    completion_percentage = Column(Float, default=0.0)  # 0.0 to 1.0

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Learning State
    status = Column(String, default="active")  # active, completed, paused, abandoned

    # Relationship
    user = relationship("User", back_populates="learning_sessions")

class WordProgress(Base):
    __tablename__ = "word_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=True)

    # Word Information
    word = Column(String, nullable=False)
    definition = Column(Text, nullable=True)
    translation = Column(String, nullable=True)
    cefr_level = Column(String, nullable=False)  # A1, A2, B1, B2, C1, C2

    # Context
    sentence = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    timestamp = Column(Float, nullable=True)  # Video timestamp

    # Learning Metrics
    encounters = Column(Integer, default=1)  # How many times encountered
    mastery_level = Column(Float, default=0.0)  # 0.0 to 1.0
    is_mastered = Column(Boolean, default=False)

    # Spaced Repetition
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    ease_factor = Column(Float, default=2.5)  # Spaced repetition ease factor
    interval_days = Column(Integer, default=1)  # Current interval
    repetitions = Column(Integer, default=0)  # Number of successful repetitions

    # Timestamps
    first_encountered = Column(DateTime(timezone=True), server_default=func.now())
    last_reviewed = Column(DateTime(timezone=True), server_default=func.now())
    mastered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    user = relationship("User", back_populates="word_progress")
    session = relationship("LearningSession", backref="word_progress_entries")

class LearningAnalytics(Base):
    __tablename__ = "learning_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Time Period
    period_type = Column(String, nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Learning Metrics
    total_study_time = Column(Integer, default=0)  # in minutes
    sessions_completed = Column(Integer, default=0)
    words_encountered = Column(Integer, default=0)
    words_mastered = Column(Integer, default=0)
    videos_started = Column(Integer, default=0)
    videos_completed = Column(Integer, default=0)

    # Performance Metrics
    average_session_time = Column(Float, default=0.0)  # in minutes
    mastery_rate = Column(Float, default=0.0)  # percentage of words mastered
    retention_rate = Column(Float, default=0.0)  # percentage of words retained

    # Learning Pattern Data
    peak_learning_hours = Column(JSON, nullable=True)  # Hours when most active
    preferred_session_length = Column(Integer, nullable=True)  # in minutes
    learning_streak = Column(Integer, default=0)

    # CEFR Level Distribution
    level_distribution = Column(JSON, nullable=True)  # A1: 20, A2: 30, etc.
    level_progress = Column(JSON, nullable=True)  # Progress within current level

    # Calculated at
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="analytics")

class VideoAnalytics(Base):
    __tablename__ = "video_analytics"

    id = Column(Integer, primary_key=True, index=True)

    # Video Information
    video_url = Column(String, nullable=False, index=True)
    video_title = Column(String, nullable=True)
    video_duration = Column(Integer, nullable=True)

    # Content Analysis
    total_words_extracted = Column(Integer, default=0)
    cefr_level_distribution = Column(JSON, nullable=True)  # Distribution of word levels
    average_difficulty = Column(Float, nullable=True)  # Average CEFR level

    # Usage Statistics
    total_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)  # Percentage who complete
    average_session_time = Column(Float, default=0.0)  # Average time spent

    # Learning Outcomes
    average_words_mastered = Column(Float, default=0.0)
    mastery_rate = Column(Float, default=0.0)  # Success rate for this video

    # Content Quality Metrics
    engagement_score = Column(Float, default=0.0)  # Derived engagement metric
    difficulty_rating = Column(Float, default=0.0)  # Perceived difficulty

    # Metadata
    first_used = Column(DateTime(timezone=True), server_default=func.now())
    last_analyzed = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic models for API
class LearningSessionResponse(BaseModel):
    id: int
    user_id: int
    video_url: str
    video_title: Optional[str]
    session_number: int
    total_sessions: int
    focus_words: Optional[List[Dict[str, Any]]]
    words_mastered: Optional[List[str]]
    session_duration: Optional[int]
    completion_percentage: float
    status: str
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class WordProgressResponse(BaseModel):
    id: int
    word: str
    cefr_level: str
    encounters: int
    mastery_level: float
    is_mastered: bool
    first_encountered: datetime
    last_reviewed: datetime
    mastered_at: Optional[datetime]

    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_study_time: int
    sessions_completed: int
    words_mastered: int
    current_streak: int
    mastery_rate: float
    average_session_time: float
    level_distribution: Dict[str, int]
    recent_activity: List[LearningSessionResponse]

class LearningInsights(BaseModel):
    weekly_progress: List[Dict[str, Any]]
    learning_patterns: Dict[str, Any]
    word_mastery_trends: List[Dict[str, Any]]
    recommendations: List[Dict[str, str]]
    achievements: List[Dict[str, str]]

# Update User model to include relationships
# This should be added to models/user.py but we'll handle it here for now
def add_user_relationships():
    """Add relationships to User model - call this after importing"""
    from .user import User
    User.learning_sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")
    User.word_progress = relationship("WordProgress", back_populates="user", cascade="all, delete-orphan")
    User.analytics = relationship("LearningAnalytics", back_populates="user", cascade="all, delete-orphan")