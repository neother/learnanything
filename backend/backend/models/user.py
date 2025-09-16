from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Profile information
    name = Column(String, nullable=False)
    estimated_level = Column(String, default="A2")  # CEFR level
    completed_assessment = Column(Boolean, default=False)

    # Learning statistics
    words_learned = Column(Integer, default=0)
    total_study_time = Column(Integer, default=0)  # in minutes
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

    # Account metadata
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True), server_default=func.now())

    # Assessment data (stored as JSON string)
    assessment_data = Column(Text, nullable=True)  # JSON string of assessment results

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

# Pydantic models for API
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    name: str
    estimated_level: str = "A2"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    name: str
    estimated_level: str
    completed_assessment: bool
    words_learned: int
    total_study_time: int
    current_streak: int
    longest_streak: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_active_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    estimated_level: Optional[str] = None
    words_learned: Optional[int] = None
    total_study_time: Optional[int] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None