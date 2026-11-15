import pytest

from app import repository
from app.security import hash_password

PASSWORD = "password"
PASSWORD_HASH = hash_password(PASSWORD)


@pytest.fixture
def user(monkeypatch):
    record = {"id": 1, "username": "alice", "password_hash": PASSWORD_HASH}
    monkeypatch.setattr(
        repository,
        "get_user",
        lambda cur, username: record if username == "alice" else None,
    )
    return record


def login(client, username, password):
    return client.post("/api/login", json={"username": username, "password": password})


def test_login_returns_bearer_token(client, user):
    response = login(client, "alice", PASSWORD)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_rejects_wrong_password(client, user):
    response = login(client, "alice", "password123")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_rejects_unknown_user(client, user):
    response = login(client, "bob", PASSWORD)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_gives_same_error_for_unknown_user_and_wrong_password(client, user):
    unknown_user = login(client, "bob", PASSWORD)
    wrong_password = login(client, "alice", "password123")

    assert unknown_user.status_code == wrong_password.status_code
    assert unknown_user.json() == wrong_password.json()


def test_login_requires_password(client, user):
    response = client.post("/api/login", json={"username": "alice"})

    assert response.status_code == 422


def test_token_from_login_grants_access(client, user, monkeypatch):
    monkeypatch.setattr(
        repository, "list_devices", lambda cur, timeout, device_id=None: []
    )
    token = login(client, "alice", PASSWORD).json()["access_token"]

    response = client.get("/api/devices", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == []