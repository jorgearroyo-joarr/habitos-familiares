"""
HábitosFam – pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import get_db
from backend import models


# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create fresh DB for each test."""
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Test client with DB override."""
    return TestClient(app)


@pytest.fixture(scope="function")
def admin_pin(db):
    """Create admin PIN for testing."""
    from backend import crud
    from backend.schemas import AppSettingsUpdate

    crud.update_app_settings(
        db,
        AppSettingsUpdate(
            admin_pin="1234",
            currency_symbol="$",
            app_name="TestApp",
            streak_bonus_days=7,
            streak_bonus_pct=1.5,
        ),
    )
    return "1234"


@pytest.fixture(scope="function")
def test_profile(db, admin_pin):
    """Create a test profile."""
    from backend.schemas import ProfileCreate

    profile = crud.create_profile(
        db,
        ProfileCreate(
            slug="test-child",
            name="Test Child",
            age=8,
            avatar="👶",
            theme="default",
            pin="0000",
            base_weekly_reward=2.0,
            full_weekly_reward=4.0,
            monthly_min_pct=0.75,
            monthly_reward_desc="Movie Night 🎬",
        ),
    )
    return profile
