"""
database.py
-------------
Database initialization file.
Sets up the SQLite connection and SQLAlchemy session machinery.
All models (in app/models/) inherit from `Base`.
Tables are created by calling init_db() once, on app startup.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./neomind.db"

# check_same_thread=False is required for SQLite when used with FastAPI's
# multi-threaded request handling.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Imports all models (so they register with Base) and creates their tables."""
    from app.models import user, study_session  # noqa: F401
    Base.metadata.create_all(bind=engine)
