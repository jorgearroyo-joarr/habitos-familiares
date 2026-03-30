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

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── App lifecycle ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: run migrations and seed default data."""
    print("DEBUG: Entering lifespan", flush=True)
    logger.info(
        "🚀 HábitosFam %s starting up (%s)",
        settings.app_version,
        settings.db_engine_type,
    )
    sys.stdout.flush()

    # Run Alembic migrations FIRST (handles both new and existing DBs)
    try:
        from alembic.config import Config
        from alembic import command

        ini_path = Path(__file__).parent.parent / "alembic.ini"
        logger.info("🛠️ Running migrations from: %s", ini_path.absolute())
        
        alembic_cfg = Config(str(ini_path))
        # Ensure alembic uses our configured database URL
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
        
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Alembic migrations completed on engine: %s", settings.db_engine_type)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        # In production, we might want to exit if migrations fail
        # raise

    # Auto-seed default profiles, habits, micro-habits, reward tiers
    from . import crud
    from .database import SessionLocal

    db = SessionLocal()
    try:
        crud.seed_default_data(db)
        db.commit()
    except Exception as e:
        logger.error(f"❌ Seed failed: {e}", exc_info=True)
        db.rollback()
        raise
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
