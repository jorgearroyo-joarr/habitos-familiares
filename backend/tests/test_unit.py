import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import crud, models, schemas
from backend.data_config import _hash_pin
from backend.database import Base

# In-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_pin_hashing():
    pin = "1234"
    hashed = _hash_pin(pin)
    assert hashed != pin
    assert len(hashed) == 64  # SHA-256 hex length

def test_verify_pin_admin(db):
    # Setup AppSettings with a known admin PIN
    admin_pin = "4321"
    hashed_admin = _hash_pin(admin_pin)
    db.add(models.AppSettings(id=1, admin_pin_hash=hashed_admin, app_name="Test App"))
    db.commit()

    result = crud.verify_pin(db, admin_pin)
    assert result is not None
    assert result["role"] == "admin"
    assert result["profile_slug"] is None

def test_create_and_get_profile(db):
    profile_data = schemas.ProfileCreate(
        slug="testchild",
        name="Test Child",
        age=5,
        pin="1111"
    )
    crud.create_profile(db, profile_data)

    profile = crud.get_profile_by_slug(db, "testchild")
    assert profile is not None
    assert profile.name == "Test Child"
    assert profile.pin_hash == _hash_pin("1111")
