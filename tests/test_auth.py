from app.main import app
from app.models import User
from app.database.connection import get_db


def test_register_success(client):
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


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Wrong Password User",
            "email": "wrong@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@test.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401


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