"""POST /api/query — re-run an already-known SQL string (e.g. the frontend's "regenerate" action)
through the same validation and execution pipeline as chat, without going back through the LLM.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.analytics import QueryRequest, QueryResult
from app.services import sql_validator
from app.services.auth_service import get_current_user
from app.services.query_service import QueryExecutionError, execute_readonly_query

router = APIRouter(prefix="/api", tags=["query"], dependencies=[Depends(get_current_user)])


@router.post("/query", response_model=QueryResult)
def run_query(payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResult:
    validation = sql_validator.validate_sql(payload.sql)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail="; ".join(validation.errors))

    try:
        result = execute_readonly_query(db, validation.sql)
    except QueryExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return QueryResult(
        columns=result.columns,
        rows=result.rows,
        row_count=result.row_count,
        truncated=result.row_count >= 1000,
    )
