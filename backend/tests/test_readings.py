from datetime import datetime, timezone

import pytest

from app import repository
from app.live import hub
from app.routers import readings

NOW = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)

PAYLOAD = {
    "device_id": "kitchen-aht20",
    "room": "kitchen",
    "type": "temp_humidity",
    "source": "sim",
    "values": {"temperature": 21.5, "humidity": 45.0},
}

DEVICE = {
    "device_id": "kitchen-aht20",
    "room": "kitchen",
    "type": "temp_humidity",
    "source": "sim",
    "last_seen": NOW,
    "online": True,
    "last_reading": {"ts": NOW, "data": {"temperature": 21.5, "humidity": 45.0}},
}


@pytest.fixture
def stored(monkeypatch):
    calls = []

    def fake_store_reading(conn, payload):
        calls.append(payload)
        return DEVICE

    monkeypatch.setattr(readings, "store_reading", fake_store_reading)
    return calls


@pytest.fixture
def broadcasts(monkeypatch):
    sent = []

    async def fake_broadcast(message):
        sent.append(message)

    monkeypatch.setattr(hub, "broadcast", fake_broadcast)
    return sent


def test_add_reading_requires_api_key(client, stored):
    response = client.post("/api/readings", json=PAYLOAD)

    assert response.status_code == 401
    assert stored == []


def test_add_reading_rejects_wrong_api_key(client, stored):
    response = client.post(
        "/api/readings", json=PAYLOAD, headers={"X-API-Key": "wrong-key"}
    )

    assert response.status_code == 401
    assert stored == []


def test_add_reading_stores_and_broadcasts(client, api_key_headers, stored, broadcasts):
    response = client.post("/api/readings", json=PAYLOAD, headers=api_key_headers)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert len(stored) == 1
    assert stored[0].device_id == "kitchen-aht20"
    assert len(broadcasts) == 1
    assert broadcasts[0]["type"] == "reading"
    assert broadcasts[0]["device"]["device_id"] == "kitchen-aht20"
    assert broadcasts[0]["device"]["last_reading"]["data"] == {
        "temperature": 21.5,
        "humidity": 45.0,
    }


def test_add_reading_rejects_unknown_type(client, api_key_headers, stored):
    response = client.post(
        "/api/readings", json={**PAYLOAD, "type": "light"}, headers=api_key_headers
    )

    assert response.status_code == 422
    assert stored == []


def test_add_reading_rejects_unknown_source(client, api_key_headers, stored):
    response = client.post(
        "/api/readings", json={**PAYLOAD, "source": "virtual"}, headers=api_key_headers
    )

    assert response.status_code == 422
    assert stored == []


def test_add_reading_hides_internal_error(
    client, api_key_headers, broadcasts, monkeypatch
):
    def failing_store_reading(conn, payload):
        raise RuntimeError("connection to database refused")

    monkeypatch.setattr(readings, "store_reading", failing_store_reading)

    response = client.post("/api/readings", json=PAYLOAD, headers=api_key_headers)

    assert response.status_code == 500
    assert "database" not in response.text
    assert broadcasts == []


def test_get_readings_requires_token(client):
    response = client.get("/api/readings", params={"device_id": "kitchen-aht20"})

    assert response.status_code == 401


def test_get_readings_requires_device_id(client, auth_headers):
    response = client.get("/api/readings", headers=auth_headers)

    assert response.status_code == 422


def test_get_readings_returns_history(client, auth_headers, monkeypatch):
    history = [{"ts": NOW, "data": {"temperature": 21.5}}]
    monkeypatch.setattr(
        repository,
        "get_readings",
        lambda cur, device_id, ts_from, ts_to, limit: history,
    )

    response = client.get(
        "/api/readings", params={"device_id": "kitchen-aht20"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["data"] == {"temperature": 21.5}


def test_get_readings_passes_filters_to_repository(client, auth_headers, monkeypatch):
    captured = {}

    def fake_get_readings(cur, device_id, ts_from, ts_to, limit):
        captured.update(device_id=device_id, limit=limit)
        return []

    monkeypatch.setattr(repository, "get_readings", fake_get_readings)

    client.get(
        "/api/readings",
        params={"device_id": "kitchen-aht20", "limit": 10},
        headers=auth_headers,
    )

    assert captured == {"device_id": "kitchen-aht20", "limit": 10}


def test_get_readings_with_bucket_uses_aggregation(client, auth_headers, monkeypatch):
    bucket_calls = []

    def fake_get_bucketed_readings(cur, device_id, ts_from, ts_to, bucket, limit):
        bucket_calls.append(bucket)
        return []

    def unexpected_get_readings(*args):
        raise AssertionError("plain history must not be used when bucket is set")

    monkeypatch.setattr(repository, "get_bucketed_readings", fake_get_bucketed_readings)
    monkeypatch.setattr(repository, "get_readings", unexpected_get_readings)

    response = client.get(
        "/api/readings",
        params={"device_id": "kitchen-aht20", "bucket": 60},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert bucket_calls == [60]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 5001}, {"bucket": 0}])
def test_get_readings_rejects_invalid_params(client, auth_headers, params):
    response = client.get(
        "/api/readings",
        params={"device_id": "kitchen-aht20", **params},
        headers=auth_headers,
    )

    assert response.status_code == 422