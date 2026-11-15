from datetime import datetime, timezone

from app import repository

NOW = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)

DEVICES = [
    {
        "device_id": "kitchen-aht20",
        "room": "kitchen",
        "type": "temp_humidity",
        "source": "sim",
        "last_seen": NOW,
        "online": True,
        "last_reading": {"ts": NOW, "data": {"temperature": 21.5, "humidity": 45.0}},
    },
    {
        "device_id": "bedroom-pir",
        "room": "bedroom",
        "type": "motion",
        "source": "sim",
        "last_seen": NOW,
        "online": False,
        "last_reading": None,
    },
]


def test_get_devices_requires_token(client):
    response = client.get("/api/devices")

    assert response.status_code == 401


def test_get_devices_rejects_invalid_token(client):
    response = client.get(
        "/api/devices", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_get_devices_returns_devices_with_last_reading(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        repository, "list_devices", lambda cur, timeout, device_id=None: DEVICES
    )

    response = client.get("/api/devices", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert [device["device_id"] for device in body] == ["kitchen-aht20", "bedroom-pir"]
    assert body[0]["online"] is True
    assert body[0]["last_reading"]["data"] == {"temperature": 21.5, "humidity": 45.0}


def test_get_devices_allows_device_without_readings(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        repository, "list_devices", lambda cur, timeout, device_id=None: DEVICES
    )

    body = client.get("/api/devices", headers=auth_headers).json()

    assert body[1]["online"] is False
    assert body[1]["last_reading"] is None


def test_get_devices_passes_online_timeout(client, auth_headers, monkeypatch):
    captured = {}

    def fake_list_devices(cur, timeout, device_id=None):
        captured["timeout"] = timeout
        return []

    monkeypatch.setattr(repository, "list_devices", fake_list_devices)

    client.get("/api/devices", headers=auth_headers)

    assert captured["timeout"] == 180