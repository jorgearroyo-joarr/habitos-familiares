"""
HábitosFam – backend/main.py
FastAPI application entry point.
Serves the REST API and static frontend files.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .database import create_tables
from .api import habits, admin

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── App lifecycle ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed default data."""
    logger.info("🚀 HábitosFam v3 starting up (%s)", settings.db_engine_type)
    create_tables()

    # Auto-seed default profiles, habits, micro-habits, reward tiers
    from .database import SessionLocal
    from . import crud
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
STATIC_DIR = Path(__file__).parent.parent   # good_habits/

# Mount admin page
@app.get("/admin", include_in_schema=False)
async def serve_admin():
    return FileResponse(STATIC_DIR / "admin.html")

# Serve index.html for root
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

# Serve all other static assets (js, css, etc.)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
