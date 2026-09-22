"""
Database connection manager with robust SQLAlchemy session handling.
Supports PostgreSQL with transparent SQLite fallback.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.config import settings

logger = logging.getLogger("mining_dt.database")

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    
    try:
        eng = create_engine(
            db_url,
            connect_args=connect_args,
            echo=False,
            pool_pre_ping=True
        )
        # Test connection
        with eng.connect() as conn:
            pass
        logger.info(f"Database connected successfully: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        return eng
    except Exception as e:
        logger.warning(f"Failed to connect to configured DB ({db_url}): {e}. Falling back to SQLite.")
        fallback_url = "sqlite:///./mining_digital_twin.db"
        eng = create_engine(fallback_url, connect_args={"check_same_thread": False}, echo=False)
        return eng

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency for yielding database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    """Returns a direct database session for use in services and Streamlit."""
    return SessionLocal()

def create_all_tables():
    """Initializes all database tables registered with Base."""
    import database.models  # Ensure all models are imported
    Base.metadata.create_all(bind=engine)
    logger.info("All database tables created or confirmed.")
