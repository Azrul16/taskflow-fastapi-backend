import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_login_and_create_task() -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    task_response = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Check PostgreSQL migration"},
    )
    assert task_response.status_code == 201
    assert task_response.json()["title"] == "Check PostgreSQL migration"


def test_invalid_token_subject_returns_unauthorized() -> None:
    from app.core.security import create_access_token

    token = create_access_token("not-an-integer")

    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
