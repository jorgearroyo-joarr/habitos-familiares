import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import crud
from backend.database import Base, get_db
from backend.main import app

# Setup test DB
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
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    crud.seed_default_data(db)
    yield
    Base.metadata.drop_all(bind=engine)

def test_public_health():
    response = client.get("/api/health-public")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login_flow():
    # Login as admin (default seed PIN 1234)
    response = client.post("/api/auth/login", json={"pin": "1234"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["role"] == "admin"

def test_fetch_profiles():
    response = client.get("/api/profiles")
    assert response.status_code == 200
    profiles = response.json()
    assert len(profiles) > 0
    assert profiles[0]["slug"] in ["alana", "sofia"]
