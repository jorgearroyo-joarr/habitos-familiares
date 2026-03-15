"""Tests for HábitosFam API - v2.2.0 Analytics and Templates."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.crud import seed_default_data


# Test database
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_default_data(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    return TestClient(app)


class TestTrends:
    """Test trend/chart endpoints."""

    def test_get_trends_weekly(self, client, db_session):
        response = client.get("/api/profiles/alana/trends?period=weekly")
        assert response.status_code == 200
        data = response.json()
        assert data["profile_slug"] == "alana"
        assert data["period"] == "weekly"
        assert "data" in data
        assert "average_pct" in data

    def test_get_trends_monthly(self, client, db_session):
        response = client.get("/api/profiles/alana/trends?period=monthly")
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "monthly"

    def test_get_trends_yearly(self, client, db_session):
        response = client.get("/api/profiles/alana/trends?period=yearly")
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "yearly"

    def test_get_trends_invalid_period(self, client, db_session):
        response = client.get("/api/profiles/alana/trends?period=invalid")
        assert response.status_code == 400

    def test_get_trends_profile_not_found(self, client, db_session):
        response = client.get("/api/profiles/nonexistent/trends")
        assert response.status_code == 404


class TestTemplatesCatalog:
    """Test habit templates catalog endpoint."""

    def test_get_templates_catalog(self, client, db_session):
        response = client.get("/api/admin/templates/catalog")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

    def test_templates_have_required_fields(self, client, db_session):
        response = client.get("/api/admin/templates/catalog")
        data = response.json()
        for cat in data["categories"]:
            assert "category" in cat
            assert "description" in cat
            assert "age_range" in cat
            assert "habits" in cat


class TestMonthClose:
    """Test month auto-close endpoint."""

    def test_close_current_month(self, client, db_session, monkeypatch):
        # Mock admin PIN
        monkeypatch.setattr("backend.crud._hash_pin", lambda x: x)
        monkeypatch.setattr("backend.data_config.DEFAULT_ADMIN_PIN", "1234")

        response = client.post(
            "/api/admin/profiles/alana/close-current-month",
            headers={"X-Admin-Pin": "1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "month_key" in data
        assert "days_completed" in data
        assert "reward_unlocked" in data

    def test_close_specific_month(self, client, db_session, monkeypatch):
        monkeypatch.setattr("backend.crud._hash_pin", lambda x: x)
        monkeypatch.setattr("backend.data_config.DEFAULT_ADMIN_PIN", "1234")

        response = client.post(
            "/api/admin/profiles/alana/close-month?month_key=2026-03",
            headers={"X-Admin-Pin": "1234"},
        )
        assert response.status_code == 200

    def test_close_month_without_auth(self, client, db_session):
        response = client.post("/api/admin/profiles/alana/close-current-month")
        assert response.status_code == 401


class TestHabitReorder:
    """Test habit reordering endpoint."""

    def test_reorder_habits(self, client, db_session, monkeypatch):
        monkeypatch.setattr("backend.crud._hash_pin", lambda x: x)
        monkeypatch.setattr("backend.data_config.DEFAULT_ADMIN_PIN", "1234")

        # First get habits
        response = client.get("/api/admin/profiles/alana/habits")
        habits = response.json()

        if len(habits) >= 2:
            # Reorder
            reorder_data = {
                "orders": [
                    {"id": habits[0]["id"], "sort_order": 1},
                    {"id": habits[1]["id"], "sort_order": 0},
                ]
            }
            response = client.post(
                "/api/admin/profiles/alana/habits/reorder",
                json=reorder_data,
                headers={"X-Admin-Pin": "1234"},
            )
            assert response.status_code == 200

    def test_reorder_without_auth(self, client, db_session):
        response = client.post(
            "/api/admin/profiles/alana/habits/reorder", json={"orders": []}
        )
        assert response.status_code == 401


class TestExistingEndpoints:
    """Verify existing endpoints still work."""

    def test_health_endpoint(self, client):
        response = client.get("/api/health-public")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_login_valid_pin(self, client, db_session):
        response = client.post("/api/auth/login", json={"pin": "1234"})
        assert response.status_code == 200
        assert response.json()["role"] in ["admin", "user"]
