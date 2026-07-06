# =====================================================================
# FILE: backend/app/db/session.py
# DESCRIPTION: Database engine initialization and session management.
# =====================================================================

import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.db.models import Base

logger = logging.getLogger(__name__)

# Ensure data directory exists
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    db_path_str = db_url.replace("sqlite:///", "")
    # Check if relative path or absolute path
    if db_path_str.startswith("../"):
        db_path = Path(__file__).resolve().parent.parent.parent / db_path_str.replace("../", "")
    else:
        db_path = Path(db_path_str)
    
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Recalculate sqlite URL if needed
    db_url = f"sqlite:///{db_path}"

logger.info(f"Database URL: {db_url}")
engine = create_engine(db_url, connect_args={"check_same_thread": False} if "sqlite" in db_url else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes tables in database."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("SQLAlchemy database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to create SQLAlchemy tables: {e}", exc_info=True)

# Create tables immediately on module load
init_db()

def get_db():
    """Dependency / Context helper to yield database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
