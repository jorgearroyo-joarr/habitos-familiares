"""
HábitosFam – backend/main.py
FastAPI application entry point.
Serves the REST API and static frontend files.
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import admin, habits
from .config import settings
from .database import create_tables, engine

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run automatic migrations for new columns."""
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            # Check if consecutive_days column exists
            result = conn.execute(
                text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'habit_templates' AND column_name = 'consecutive_days'
            """)
            )
            if result.fetchone() is None:
                logger.info("📊 Adding consecutive_days column to habit_templates...")
                conn.execute(
                    text(
                        "ALTER TABLE habit_templates ADD COLUMN consecutive_days INTEGER DEFAULT 0"
                    )
                )
                conn.commit()
                logger.info("✅ Added consecutive_days column")

            # Check if is_mastered column exists
            result = conn.execute(
                text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'habit_templates' AND column_name = 'is_mastered'
            """)
            )
            if result.fetchone() is None:
                logger.info("📊 Adding is_mastered column to habit_templates...")
                conn.execute(
                    text(
                        "ALTER TABLE habit_templates ADD COLUMN is_mastered BOOLEAN DEFAULT FALSE"
                    )
                )
                conn.commit()
                logger.info("✅ Added is_mastered column")

            # Check if mastered_at column exists
            result = conn.execute(
                text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'habit_templates' AND column_name = 'mastered_at'
            """)
            )
            if result.fetchone() is None:
                logger.info("📊 Adding mastered_at column to habit_templates...")
                conn.execute(
                    text("ALTER TABLE habit_templates ADD COLUMN mastered_at TIMESTAMP")
                )
                conn.commit()
                logger.info("✅ Added mastered_at column")

    except Exception as e:
        logger.warning(f"Migration check warning: {e}")


# ── App lifecycle ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed default data."""
    print("DEBUG: Entering lifespan", flush=True)
    logger.info("🚀 HábitosFam v3 starting up (%s)", settings.db_engine_type)
    sys.stdout.flush()

    try:
        logger.info("📡 Initializing database tables...")
        sys.stdout.flush()
        create_tables()
        logger.info("✅ Database tables created/verified")
        sys.stdout.flush()
    except Exception as e:
        logger.error("❌ FAILED to create tables: %s", e, exc_info=True)
        sys.stdout.flush()
        raise

    # Run migrations for new columns
    run_migrations()

    # Auto-seed default profiles, habits, micro-habits, reward tiers
    from . import crud
    from .database import SessionLocal

    db = SessionLocal()
    try:
        crud.seed_default_data(db)
    finally:
        db.close()

    logger.info("✅ Startup complete — http://localhost:%d", settings.port)
    yield
    logger.info("👋 HábitosFam shutting down")


# ── FastAPI app ────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema familiar de buenos hábitos — REST API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production: settings.cors_origins_list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ─────────────────────────────────────────────────
app.include_router(habits.router)
app.include_router(admin.router)


# ── Health (no auth needed) ─────────────────────────────────────
@app.get("/api/health-public")
def public_health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "db": settings.db_engine_type,
    }


# ── Static files (serve frontend from project root) ─────────────
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"

# Determine which directory to serve (dist if it exists, otherwise source)
STATIC_DIR = DIST_DIR if DIST_DIR.exists() else FRONTEND_DIR

logger.info("📂 Serving static files from: %s", STATIC_DIR.absolute())


# Mount admin page
@app.get("/admin", include_in_schema=False)
async def serve_admin():
    return FileResponse(STATIC_DIR / "admin.html")


# Serve index.html for root
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


# Serve favicon at root
@app.get("/favicon.svg", include_in_schema=False)
async def serve_favicon_svg():
    target = STATIC_DIR / "public" / "favicon.svg"
    if not target.exists():
        target = STATIC_DIR / "favicon.svg"
    return FileResponse(target)


@app.get("/favicon.ico", include_in_schema=False)
async def serve_favicon_ico():
    target = STATIC_DIR / "public" / "favicon.svg"
    if not target.exists():
        target = STATIC_DIR / "favicon.svg"
    return FileResponse(target)


# Serve all other static assets (js, css, etc.)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
