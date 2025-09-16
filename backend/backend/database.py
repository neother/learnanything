from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database for simplicity (can be upgraded to PostgreSQL later)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learnanything.db")

# Create engine
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=False  # Set to True for SQL debugging
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    # Import all models here
    from models.user import Base
    from models.analytics import LearningSession, WordProgress, LearningAnalytics, VideoAnalytics, add_user_relationships

    # Add relationships to User model
    add_user_relationships()

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")