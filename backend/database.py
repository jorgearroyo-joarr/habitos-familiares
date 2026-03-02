"""
HábitosFam – backend/database.py
SQLAlchemy database abstraction layer.

IMPORTANT: This is the ONLY file that needs to change when switching DBs.
Change DATABASE_URL in .env to migrate between:
  - SQLite:      sqlite:///./habitosfam.db
  - PostgreSQL:  postgresql://user:pass@host:5432/habitosfam
  - MySQL:       mysql+pymysql://user:pass@host:3306/habitosfam
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from typing import Generator
from .config import settings
import logging

logger = logging.getLogger(__name__)


# ── Engine factory ────────────────────────────────────────────
def _build_engine():
    """
    Builds the SQLAlchemy engine based on DATABASE_URL.
    SQLite uses StaticPool for single-file thread safety.
    PostgreSQL / MySQL use the default connection pool.
    """
    url = settings.database_url

    if settings.is_sqlite:
        # SQLite-specific: connect_args for thread safety with FastAPI
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.debug,
        )
        # Enable WAL mode for better concurrent read performance
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, _connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        logger.info("📁 SQLite engine created at: %s", url)

    elif "postgresql" in url or "postgres" in url:
        engine = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,   # detect stale connections
            echo=settings.debug,
        )
        logger.info("🐘 PostgreSQL engine created")

    else:  # MySQL
        engine = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=settings.debug,
        )
        logger.info("🐬 MySQL engine created")

    return engine


# ── Singleton engine & session ────────────────────────────────
engine = _build_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ── Base model class ──────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this."""
    pass


# ── FastAPI dependency ────────────────────────────────────────
def get_db() -> Generator:
    """
    Dependency injected into FastAPI route handlers.
    Yields a DB session and ensures it's closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all tables if they don't exist (runs on startup)."""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified (engine: %s)", settings.db_engine_type)


def drop_tables():
    """Drop all tables — use only in dev/testing."""
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️ All tables dropped!")
