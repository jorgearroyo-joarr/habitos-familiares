"""
HábitosFam – API Endpoint Tests
"""

import pytest


class TestPublicEndpoints:
    """Tests for public (unauthenticated) endpoints."""

    def test_settings_endpoint(self, client):
        """Settings should be accessible without auth."""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "currency_symbol" in data
        assert "app_name" in data

    def test_list_profiles_empty(self, client):
        """Profiles list should work without auth."""
        response = client.get("/api/profiles")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_nonexistent_profile(self, client):
        """Should return 404 for nonexistent profile."""
        response = client.get("/api/profiles/nonexistent")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]

    def test_invalid_pin_login(self, client):
        """Invalid PIN should return 401."""
        response = client.post("/api/auth/login", json={"pin": "9999"})
        assert response.status_code == 401


class TestProfileIsolation:
    """Tests ensuring profile data isolation."""

    def test_profile_data_isolation(self, client, test_profile):
        """Requesting one profile should not return others."""
        response = client.get("/api/profiles/test-child")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test-child"

        # Try to access nonexistent profile
        response2 = client.get("/api/profiles/other-child")
        assert response2.status_code == 404


class TestHabitFlow:
    """Tests for habit tracking flow."""

    def test_habits_config_requires_valid_profile(self, client):
        """Habits config should require valid profile."""
        response = client.get("/api/profiles/invalid/habits-config")
        assert response.status_code == 404

    def test_today_log_requires_valid_profile(self, client):
        """Today log should require valid profile."""
        response = client.get("/api/profiles/invalid/today")
        assert response.status_code == 404


class TestAdminEndpoints:
    """Tests for admin-protected endpoints."""

    def test_admin_requires_pin(self, client):
        """Admin endpoints should require PIN."""
        response = client.get("/api/admin/settings")
        assert response.status_code == 401

    def test_admin_login_invalid_pin(self, client):
        """Admin login should reject invalid PIN."""
        response = client.post("/api/admin/login", json={"pin": "0000"})
        assert response.status_code == 401

    def test_admin_login_valid_pin(self, client, admin_pin):
        """Admin login should succeed with valid PIN."""
        response = client.post("/api/admin/login", json={"pin": admin_pin})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["role"] == "admin"

    def test_admin_create_profile(self, client, admin_pin):
        """Admin should be able to create profiles."""
        response = client.post(
            "/api/admin/profiles",
            json={
                "slug": "new-child",
                "name": "New Child",
                "age": 6,
                "avatar": "🧒",
                "theme": "default",
                "pin": "1111",
                "base_weekly_reward": 2.0,
                "full_weekly_reward": 4.0,
                "monthly_min_pct": 0.75,
                "monthly_reward_desc": "Pizza 🍕",
            },
            headers={"X-Admin-Pin": admin_pin},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "new-child"
