from unittest.mock import AsyncMock

import pytest
from datetime import datetime, timedelta, timezone
from app.main import app
from app.models import User
from app.database.connection import get_db


@pytest.fixture(autouse=True)
def mock_verification_email(monkeypatch):
    mock = AsyncMock()

    monkeypatch.setattr(
        "app.routes.auth.send_verification_email",
        mock
    )

    return mock

def test_register_success(client, mock_verification_email):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Candidate",
            "email": "candidate@test.com",
            "password": "TestPassword123",
            "role": "candidate",
            "phone_number": "9876543210"
        }
    )

    assert response.status_code == 201
    assert response.json()["email"] == "candidate@test.com"
    assert response.json()["role"] == "candidate"
    assert response.json()["phone_number"] == "9876543210"
    assert "password_hash" not in response.json()

    mock_verification_email.assert_awaited_once()


def test_register_duplicate_email(client):
    user_data = {
        "full_name": "Test Candidate",
        "email": "duplicate@test.com",
        "password": "TestPassword123",
        "role": "candidate"
    }

    client.post("/api/v1/auth/register", json=user_data)

    response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Login Candidate",
            "email": "login@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@test.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Login Candidate",
            "email": "login@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    user = db.query(User).filter(
        User.email == "login@test.com"
    ).first()

    verification_token = user.email_verification_token
    db_generator.close()

    verify_response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": verification_token}
    )

    assert verify_response.status_code == 200

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@test.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_register_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "invalid-email",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "short@test.com",
            "password": "123",
            "role": "candidate"
        }
    )

    assert response.status_code == 422


def test_register_invalid_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "role@test.com",
            "password": "TestPassword123",
            "role": "admin"
        }
    )

    assert response.status_code == 422

from app.models import User
from app.core.security import hash_password
from app.database.connection import SessionLocal

def test_login_inactive_account(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Inactive User",
            "email": "inactive@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    from app.database.connection import get_db

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    user = db.query(User).filter(
        User.email == "inactive@test.com"
    ).first()

    user.is_active = False
    db.commit()

    db_generator.close()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive@test.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is inactive"

import pytest


@pytest.fixture(autouse=True)
def mock_verification_email(monkeypatch):
    mock = AsyncMock()

    monkeypatch.setattr(
        "app.routes.auth.send_verification_email",
        mock
    )

    return mock

def test_verify_email_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Verify Candidate",
            "email": "verify@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    user = db.query(User).filter(
        User.email == "verify@test.com"
    ).first()

    verification_token = user.email_verification_token

    db_generator.close()

    response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": verification_token}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    user = db.query(User).filter(
        User.email == "verify@test.com"
    ).first()

    assert user.is_verified is True
    assert user.email_verification_token is None
    assert user.email_verification_expires is None

    db_generator.close()

def test_verify_email_invalid_token(client):
    response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": "invalid-token"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid verification token"

def test_verify_email_expired_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Expired Candidate",
            "email": "expired@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    user = db.query(User).filter(
        User.email == "expired@test.com"
    ).first()

    verification_token = user.email_verification_token
    user.email_verification_expires = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    )
    db.commit()
    db_generator.close()

    response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": verification_token}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verification token has expired"

def test_login_unverified_user(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Unverified Candidate",
            "email": "unverified@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unverified@test.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Please verify your email before logging in"
    )