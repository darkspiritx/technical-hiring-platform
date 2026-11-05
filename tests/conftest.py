import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import Base, get_db

# In-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

@pytest.fixture(autouse=True)
def mock_verification_email(monkeypatch):

    async def fake_send_verification_email(to_email, verification_token):
        db_generator = app.dependency_overrides[get_db]()
        db = next(db_generator)

        try:
            from app.models import User

            user = db.query(User).filter(
                User.email == to_email
            ).first()

            if user:
                user.is_verified = True
                user.email_verification_token = None
                user.email_verification_expires = None
                db.commit()

        finally:
            db_generator.close()

    monkeypatch.setattr(
        "app.routes.auth.send_verification_email",
        fake_send_verification_email
    )
    
@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)