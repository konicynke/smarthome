import os

os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "smarthome_test"
os.environ["POSTGRES_PASSWORD"] = "smarthome_test"
os.environ["POSTGRES_DB"] = "smarthome_test"
os.environ["JWT_SECRET"] = "test-jwt-secret-for-unit-tests-123"
os.environ["API_KEY"] = "test-api-key"
os.environ["ONLINE_TIMEOUT_SECONDS"] = "180"

import pytest
from fastapi.testclient import TestClient

from app.db import get_conn
from app.main import app
from app.security import create_token




class FakeCursor:
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class FakeConnection:
    def cursor(self):
        return FakeCursor()


@pytest.fixture
def client():
    app.dependency_overrides[get_conn] = lambda: FakeConnection()
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {create_token('alice')}"}


@pytest.fixture
def api_key_headers():
    return {"X-API-Key": os.environ["API_KEY"]}