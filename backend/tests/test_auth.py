"""Registration/login/session tests."""
import uuid

from fastapi.testclient import TestClient


def _random_email() -> str:
    return f"pytest-{uuid.uuid4().hex[:12]}@example.com"


def test_register_returns_token(client: TestClient) -> None:
    email = _random_email()
    r = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"})
    assert r.status_code == 201
    body = r.json()
    assert body["access_token"]
    assert body["user"]["email"] == email


def test_register_rejects_short_password(client: TestClient) -> None:
    r = client.post("/api/auth/register", json={"email": _random_email(), "password": "short"})
    assert r.status_code == 422


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    email = _random_email()
    r1 = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"})
    assert r1.status_code == 201
    r2 = client.post("/api/auth/register", json={"email": email, "password": "anotherpassword"})
    assert r2.status_code == 409


def test_login_succeeds_with_correct_password(client: TestClient) -> None:
    email = _random_email()
    client.post("/api/auth/register", json={"email": email, "password": "supersecret1"})
    r = client.post("/api/auth/login", json={"email": email, "password": "supersecret1"})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_login_rejects_wrong_password(client: TestClient) -> None:
    email = _random_email()
    client.post("/api/auth/register", json={"email": email, "password": "supersecret1"})
    r = client.post("/api/auth/login", json={"email": email, "password": "wrongpassword"})
    assert r.status_code == 401


def test_login_rejects_unknown_email(client: TestClient) -> None:
    r = client.post("/api/auth/login", json={"email": _random_email(), "password": "whatever123"})
    assert r.status_code == 401


def test_me_requires_valid_token(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}).status_code == 401


def test_me_returns_current_user(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert "@" in r.json()["email"]
