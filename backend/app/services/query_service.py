"""Executes validated, read-only SQL against PostgreSQL and returns structured results."""
import logging
import time
from dataclasses import dataclass, field

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings

logger = logging.getLogger(__name__)


class QueryExecutionError(Exception):
    """Raised for database errors, timeouts, or other execution failures."""


@dataclass
class QueryExecutionResult:
    columns: list[str]
    rows: list[dict]
    row_count: int
    execution_ms: float
    dataframe: pd.DataFrame = field(repr=False)


def execute_readonly_query(db: Session, sql: str) -> QueryExecutionResult:
    """Runs `sql` (already validated by sql_validator) inside a read-only, time-limited transaction."""
    settings = get_settings()
    start = time.perf_counter()
    try:
        # Belt-and-suspenders: even though sql_validator only allows SELECT/WITH, force the
        # session itself to reject writes and cap how long a runaway query can hold a connection.
        db.execute(text("SET TRANSACTION READ ONLY"))
        db.execute(text(f"SET LOCAL statement_timeout = {settings.query_timeout_seconds * 1000}"))
        result = db.execute(text(sql))
        columns = list(result.keys())
        raw_rows = result.fetchall()
        db.rollback()  # read-only transaction; nothing to commit, and this releases the txn promptly
    except SQLAlchemyError as exc:
        db.rollback()
        message = str(getattr(exc, "orig", exc))
        if "statement timeout" in message.lower() or "canceling statement" in message.lower():
            raise QueryExecutionError(
                f"The query took too long and was cancelled (timeout: {settings.query_timeout_seconds}s)."
            ) from exc
        logger.warning("Query execution failed: %s", message)
        raise QueryExecutionError(f"The database rejected the query: {message}") from exc

    rows = [dict(zip(columns, r)) for r in raw_rows]
    df = pd.DataFrame(rows, columns=columns)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return QueryExecutionResult(
        columns=columns,
        rows=rows,
        row_count=len(rows),
        execution_ms=elapsed_ms,
        dataframe=df,
    )
