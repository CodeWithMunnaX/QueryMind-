"""SQL validation and security tests — no network/LLM calls, but does need a live schema
(the `sales` table) to validate column/table names against, so it uses the configured DATABASE_URL.
"""
import pytest

from app.services.sql_validator import validate_sql


class TestReadOnlyEnforcement:
    @pytest.mark.parametrize(
        "sql",
        [
            "DROP TABLE sales",
            "DELETE FROM sales",
            "UPDATE sales SET sales = 0",
            "INSERT INTO sales (order_id) VALUES ('x')",
            "ALTER TABLE sales ADD COLUMN hacked INT",
            "TRUNCATE TABLE sales",
        ],
    )
    def test_rejects_write_statements(self, sql: str) -> None:
        result = validate_sql(sql)
        assert result.is_valid is False

    def test_rejects_multiple_statements(self) -> None:
        result = validate_sql("SELECT * FROM sales; DROP TABLE sales;")
        assert result.is_valid is False
        assert any("multiple" in e.lower() for e in result.errors)

    def test_rejects_dangerous_function(self) -> None:
        result = validate_sql("SELECT pg_sleep(10)")
        assert result.is_valid is False

    def test_rejects_empty_sql(self) -> None:
        result = validate_sql("   ")
        assert result.is_valid is False

    def test_rejects_unparseable_sql(self) -> None:
        result = validate_sql("SELEKT * FRUM sales")
        assert result.is_valid is False


class TestSchemaValidation:
    def test_rejects_unknown_table(self) -> None:
        result = validate_sql("SELECT * FROM nonexistent_table")
        assert result.is_valid is False
        assert any("unknown or unauthorized table" in e.lower() for e in result.errors)

    def test_rejects_internal_app_table(self) -> None:
        # query_history/conversation_messages exist in the DB but must never be user-queryable.
        result = validate_sql("SELECT * FROM query_history")
        assert result.is_valid is False

    def test_rejects_hallucinated_column(self) -> None:
        result = validate_sql("SELECT department, SUM(sales) FROM sales GROUP BY department")
        assert result.is_valid is False
        assert any("department" in e.lower() for e in result.errors)


class TestValidQueries:
    def test_accepts_simple_select(self) -> None:
        result = validate_sql("SELECT * FROM sales LIMIT 5")
        assert result.is_valid is True
        assert result.sql

    def test_accepts_aggregate_group_by(self) -> None:
        result = validate_sql(
            "SELECT category, SUM(sales) AS total_sales FROM sales GROUP BY category ORDER BY total_sales DESC"
        )
        assert result.is_valid is True

    def test_accepts_cte(self) -> None:
        result = validate_sql(
            "WITH by_region AS (SELECT region, SUM(sales) AS total_sales FROM sales GROUP BY region) "
            "SELECT * FROM by_region ORDER BY total_sales DESC"
        )
        assert result.is_valid is True

    def test_caps_row_limit(self) -> None:
        result = validate_sql("SELECT * FROM sales LIMIT 999999")
        assert result.is_valid is True
        assert "999999" not in result.sql

    def test_adds_row_limit_when_missing(self) -> None:
        result = validate_sql("SELECT * FROM sales")
        assert result.is_valid is True
        assert "limit" in result.sql.lower()
