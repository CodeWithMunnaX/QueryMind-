"""API endpoint tests. Chat tests require OPENAI_API_KEY + DATABASE_URL and are skipped otherwise.
All data endpoints require auth — see the `auth_headers` fixture in conftest.py.
"""
import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["database"] == "connected"


def test_data_endpoints_require_auth(client: TestClient) -> None:
    for path in ("/api/schema", "/api/datasets", "/api/dashboard", "/api/history"):
        r = client.get(path)
        assert r.status_code == 401, path


def test_schema_exposes_sales_table_only(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/api/schema", headers=auth_headers)
    assert r.status_code == 200
    tables = {t["name"] for t in r.json()["tables"]}
    assert tables == {"sales"}


def test_datasets(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/api/datasets", headers=auth_headers)
    assert r.status_code == 200
    datasets = r.json()
    assert len(datasets) == 1
    assert datasets[0]["row_count"] > 0


def test_dashboard_metrics_are_live_not_hardcoded(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/api/dashboard", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["metrics"]["total_orders"] > 0
    assert body["metrics"]["total_sales"] > 0
    assert len(body["sales_by_category"]) > 0
    assert len(body["top_products"]) > 0


def test_query_endpoint_executes_valid_sql(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.post(
        "/api/query",
        json={"sql": "SELECT category, SUM(sales) AS total_sales FROM sales GROUP BY category"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert "category" in body["columns"]
    assert body["row_count"] > 0


def test_query_endpoint_rejects_dangerous_sql(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.post("/api/query", json={"sql": "DROP TABLE sales"}, headers=auth_headers)
    assert r.status_code == 400


def test_history_endpoint(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/api/history", headers=auth_headers)
    assert r.status_code == 200
    assert "items" in r.json()


def test_history_is_isolated_per_user(client: TestClient, has_llm: bool) -> None:
    if not has_llm:
        pytest.skip("OPENAI_API_KEY not configured")

    import uuid

    def register() -> dict[str, str]:
        email = f"pytest-{uuid.uuid4().hex[:12]}@example.com"
        resp = client.post("/api/auth/register", json={"email": email, "password": "pytest-password-123"})
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    user_a_headers, user_b_headers = register(), register()

    client.post(
        "/api/chat",
        json={"message": "What are total sales by region?", "conversation_id": "isolation-test"},
        headers=user_a_headers,
    )

    a_history = client.get("/api/history", headers=user_a_headers).json()["items"]
    b_history = client.get("/api/history", headers=user_b_headers).json()["items"]

    assert any(item["question"] == "What are total sales by region?" for item in a_history)
    assert not any(item["question"] == "What are total sales by region?" for item in b_history)


def test_chat_happy_path(client: TestClient, has_llm: bool, auth_headers: dict[str, str]) -> None:
    if not has_llm:
        pytest.skip("OPENAI_API_KEY not configured")
    r = client.post(
        "/api/chat",
        json={"message": "Which category generated the highest revenue in 2025?", "conversation_id": "pytest-happy"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["metadata"]["status"] == "ok"
    assert body["sql"]
    assert body["data"]


def test_chat_rejects_hallucinated_dimension(client: TestClient, has_llm: bool, auth_headers: dict[str, str]) -> None:
    if not has_llm:
        pytest.skip("OPENAI_API_KEY not configured")
    r = client.post(
        "/api/chat",
        json={"message": "Show revenue by department.", "conversation_id": "pytest-hallucination"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["metadata"]["status"] == "unanswerable"


def test_chat_handles_ambiguous_question(client: TestClient, has_llm: bool, auth_headers: dict[str, str]) -> None:
    if not has_llm:
        pytest.skip("OPENAI_API_KEY not configured")
    r = client.post(
        "/api/chat",
        json={"message": "Show me the best products.", "conversation_id": "pytest-ambiguous"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["metadata"]["status"] == "clarification_needed"
