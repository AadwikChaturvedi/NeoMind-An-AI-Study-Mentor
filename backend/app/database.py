"""
database.py
-------------
Database initialization file.
Sets up the SQLite connection and SQLAlchemy session machinery.
All models (in app/models/) inherit from `Base`.
Tables are created by calling init_db() once, on app startup.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Absolute path, resolved from this file's own location rather than the
# current working directory — otherwise the DB file's location silently
# depends on whether uvicorn was launched from backend/ or from the
# project root with --app-dir backend, which can leave you looking at
# two different (seemingly empty) databases.
DB_PATH = Path(__file__).resolve().parent.parent / "neomind.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

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
