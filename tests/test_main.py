from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_platform_info():
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    assert response.json()["backend"] == "FastAPI"
    assert response.json()["database"] == "PostgreSQL"