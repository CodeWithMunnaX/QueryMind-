import uuid

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def has_llm() -> bool:
    return bool(get_settings().openai_api_key)


@pytest.fixture(scope="session")
def auth_headers(client: TestClient) -> dict[str, str]:
    """Registers a throwaway test user and returns an Authorization header for it."""
    email = f"pytest-{uuid.uuid4().hex[:12]}@example.com"
    resp = client.post("/api/auth/register", json={"email": email, "password": "pytest-password-123"})
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
